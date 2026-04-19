"""
AttemptEvaluator: grades a QuizAttempt and computes results.
Called by the /submit/ endpoint.
"""
from decimal import Decimal
from django.utils.timezone import now
from .models import QuizAttempt, QuestionResponse


class AttemptEvaluator:
    def evaluate(self, attempt: QuizAttempt) -> dict:
        responses = attempt.responses.select_related(
            'quiz_question__question'
        ).prefetch_related('selected_options').all()

        total_marks = Decimal('0')
        obtained = Decimal('0')
        correct = wrong = skipped = 0

        for resp in responses:
            qq = resp.quiz_question
            question = qq.question
            marks_c = qq.effective_marks_correct()
            marks_w = qq.effective_marks_wrong()

            total_marks += marks_c

            if resp.visit_status in ('NOT_VISITED', 'VISITED'):
                skipped += 1
                continue

            awarded, is_correct = self._grade(resp, question, marks_c, marks_w)
            resp.marks_awarded = awarded
            resp.is_correct = is_correct
            resp.save(update_fields=['marks_awarded', 'is_correct'])

            obtained += awarded

            if is_correct is True:
                correct += 1
            elif awarded < 0:
                wrong += 1
            else:
                skipped += 1  # no penalty (e.g. partial, or integer wrong)

        # Update the attempt
        attempt.marks_obtained = obtained
        attempt.total_marks = total_marks
        attempt.correct_count = correct
        attempt.wrong_count = wrong
        attempt.skipped_count = skipped
        attempt.status = 'SUBMITTED'
        attempt.submitted_at = now()
        if total_marks > 0:
            percentage = (obtained / total_marks) * 100
            attempt.is_passed = percentage >= attempt.quiz.pass_percentage
        else:
            attempt.is_passed = False
        attempt.save()

        self._compute_rank(attempt)

        return {
            'marks_obtained': float(obtained),
            'total_marks': float(total_marks),
            'correct': correct,
            'wrong': wrong,
            'skipped': skipped,
            'is_passed': attempt.is_passed,
            'rank': attempt.rank,
        }

    def _grade(self, resp, question, marks_c, marks_w):
        q_type = question.q_type

        if q_type == 'MCQ_SINGLE':
            selected = resp.selected_options.all()
            if not selected:
                return Decimal('0'), None
            correct_opt = question.options.filter(is_correct=True).first()
            if correct_opt and selected.first().id == correct_opt.id:
                return marks_c, True
            return marks_w, False

        elif q_type == 'MCQ_MULTI':
            selected_ids = set(resp.selected_options.values_list('id', flat=True))
            correct_ids = set(question.options.filter(is_correct=True).values_list('id', flat=True))

            if not selected_ids:
                return Decimal('0'), None
            if selected_ids == correct_ids:
                return marks_c, True
            overlap = selected_ids & correct_ids
            if overlap and not (selected_ids - correct_ids):
                # Partial: selected only correct options (subset), no wrong ones
                partial = marks_c * Decimal(len(overlap)) / Decimal(len(correct_ids))
                return partial.quantize(Decimal('0.01')), None
            return marks_w, False

        elif q_type == 'INTEGER':
            # The "correct answer" is stored in a QuestionOption with is_correct=True
            correct_opt = question.options.filter(is_correct=True).first()
            if correct_opt and resp.integer_answer is not None:
                if resp.integer_answer == Decimal(correct_opt.text):
                    return marks_c, True
            return Decimal('0'), False  # no negative marking for integer type

        elif q_type == 'FILL_BLANK':
            correct_opt = question.options.filter(is_correct=True).first()
            if correct_opt and resp.integer_answer is not None:
                try:
                    if resp.integer_answer == Decimal(correct_opt.text):
                        return marks_c, True
                except Exception:
                    pass
            return Decimal('0'), False

        elif q_type == 'SUBJECTIVE':
            # Cannot auto-grade; flag for manual review
            resp.is_manually_graded = True
            resp.save(update_fields=['is_manually_graded'])
            return Decimal('0'), None

        return Decimal('0'), None

    def _compute_rank(self, attempt: QuizAttempt):
        """Rank = number of submitted attempts with strictly higher marks + 1."""
        rank = QuizAttempt.objects.filter(
            quiz=attempt.quiz,
            status='SUBMITTED',
            marks_obtained__gt=attempt.marks_obtained,
        ).count() + 1
        attempt.rank = rank
        attempt.save(update_fields=['rank'])
