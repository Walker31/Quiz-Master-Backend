from django.core.management.base import BaseCommand
from quizzes.models import Quiz, Question


class Command(BaseCommand):
    help = 'Seed JEE-level questions for all quizzes based on subject and chapter'

    # JEE-level questions organized by subject and chapter
    JEE_QUESTIONS = {
        'Mathematics': {
            'Algebra': [
                {
                    'statement': 'If α and β are roots of x² - 5x + 6 = 0, then α³ + β³ equals:',
                    'options': ['35', '30', '25', '40'],
                    'correct': 1,
                },
                {
                    'statement': 'The number of real roots of the equation x⁴ - 5x² + 4 = 0 is:',
                    'options': ['2', '4', '3', '1'],
                    'correct': 2,
                },
                {
                    'statement': 'If |x - 2| < 3, then x lies in the interval:',
                    'options': ['(-∞, 5)', '(-1, 5)', '(2, 5)', '(-1, 2)'],
                    'correct': 2,
                },
                {
                    'statement': 'Sum of first n odd numbers equals:',
                    'options': ['n(n+1)', 'n²', 'n(2n+1)', '2n²'],
                    'correct': 2,
                },
                {
                    'statement': 'If log₂(x) + log₄(x) = 3, then x equals:',
                    'options': ['4', '8', '16', '2'],
                    'correct': 3,
                },
            ],
            'Calculus': [
                {
                    'statement': 'The derivative of x²sin(x) with respect to x is:',
                    'options': ['2x·sin(x) + x²·cos(x)', 'x·sin(x)', '2x + cos(x)', 'sin(x) + x·cos(x)'],
                    'correct': 1,
                },
                {
                    'statement': 'The limit of (sin x)/x as x → 0 equals:',
                    'options': ['0', '1', '∞', 'undefined'],
                    'correct': 2,
                },
                {
                    'statement': '∫(3x² + 2x) dx equals:',
                    'options': ['x³ + x² + C', '3x³ + 2x² + C', 'x³ + x + C', '6x + 2 + C'],
                    'correct': 1,
                },
                {
                    'statement': 'The second derivative of x⁴ - 3x² + 5 is:',
                    'options': ['4x³ - 6x', '12x² - 6', '4x - 6', '12x² - 3'],
                    'correct': 2,
                },
                {
                    'statement': 'Maximum value of sin(x) + cos(x) is:',
                    'options': ['1', '√2', '2', '1/√2'],
                    'correct': 2,
                },
            ],
            'Geometry': [
                {
                    'statement': 'The distance between points (3, 4) and (0, 0) is:',
                    'options': ['5', '7', '3', '√7'],
                    'correct': 1,
                },
                {
                    'statement': 'The equation of a circle with center (2, -1) and radius 3 is:',
                    'options': ['(x-2)² + (y+1)² = 9', '(x+2)² + (y-1)² = 9', '(x-2)² + (y-1)² = 9', '(x+2)² + (y+1)² = 9'],
                    'correct': 1,
                },
                {
                    'statement': 'The area of a triangle with vertices (0,0), (3,0), (0,4) is:',
                    'options': ['6', '12', '5', '7'],
                    'correct': 1,
                },
                {
                    'statement': 'The slope of the line perpendicular to 2x + 3y = 6 is:',
                    'options': ['3/2', '-2/3', '-3/2', '2/3'],
                    'correct': 1,
                },
                {
                    'statement': 'In a triangle ABC, if ∠A = 60°, ∠B = 45°, then ∠C equals:',
                    'options': ['75°', '60°', '45°', '90°'],
                    'correct': 1,
                },
            ],
            'Statistics': [
                {
                    'statement': 'The mean of 5, 10, 15, 20, 25 is:',
                    'options': ['15', '20', '10', '25'],
                    'correct': 1,
                },
                {
                    'statement': 'The median of 2, 4, 6, 8, 10 is:',
                    'options': ['6', '4', '8', '5'],
                    'correct': 1,
                },
                {
                    'statement': 'Variance of 2, 2, 2, 2 is:',
                    'options': ['0', '1', '2', '4'],
                    'correct': 1,
                },
                {
                    'statement': 'If P(A) = 0.3 and P(B) = 0.4, then P(A∩B) can be at most:',
                    'options': ['0.3', '0.4', '0.7', '1'],
                    'correct': 1,
                },
                {
                    'statement': 'The probability of getting a sum of 7 when two dice are thrown is:',
                    'options': ['1/6', '1/12', '1/36', '5/36'],
                    'correct': 1,
                },
            ],
        },
        'Physics': {
            'Mechanics': [
                {
                    'statement': 'If a body is thrown vertically upward with velocity 20 m/s, its time of flight is (g = 10 m/s²):',
                    'options': ['2 s', '4 s', '6 s', '8 s'],
                    'correct': 2,
                },
                {
                    'statement': 'Newton\'s second law of motion is:',
                    'options': ['F = ma', 'F = mv', 'F = m/a', 'F = a/m'],
                    'correct': 1,
                },
                {
                    'statement': 'The SI unit of momentum is:',
                    'options': ['kg·m/s', 'kg/s', 'm/s', 'N·s'],
                    'correct': 1,
                },
                {
                    'statement': 'Work done is zero when the angle between force and displacement is:',
                    'options': ['90°', '0°', '45°', '60°'],
                    'correct': 1,
                },
                {
                    'statement': 'Kinetic energy of an object with mass 2 kg moving at 5 m/s is:',
                    'options': ['25 J', '50 J', '10 J', '20 J'],
                    'correct': 1,
                },
            ],
            'Thermodynamics': [
                {
                    'statement': 'Absolute zero temperature is:',
                    'options': ['-273.15°C', '0°C', '100°C', '-100°C'],
                    'correct': 1,
                },
                {
                    'statement': 'The first law of thermodynamics relates:',
                    'options': ['Heat, Work, Internal Energy', 'Force, Mass, Acceleration', 'Charge, Current, Resistance', 'Pressure, Volume, Temperature'],
                    'correct': 1,
                },
                {
                    'statement': 'Heat capacity is defined as:',
                    'options': ['Q/ΔT', 'Q×ΔT', 'Q/m', 'mΔT'],
                    'correct': 1,
                },
                {
                    'statement': 'The efficiency of a Carnot engine depends on:',
                    'options': ['Hot and cold reservoir temperatures', 'Working substance', 'Pressure', 'Volume'],
                    'correct': 1,
                },
                {
                    'statement': 'Entropy of an isolated system:',
                    'options': ['Always increases', 'Decreases', 'Remains constant', 'Becomes zero'],
                    'correct': 1,
                },
            ],
            'Electromagnetism': [
                {
                    'statement': 'The SI unit of electric field is:',
                    'options': ['N/C', 'C/N', 'V/m', 'Both A and C'],
                    'correct': 4,
                },
                {
                    'statement': 'Coulomb\'s law states F is proportional to:',
                    'options': ['q₁q₂/r', 'q₁q₂/r²', 'q₁q₂×r', 'r²/(q₁q₂)'],
                    'correct': 2,
                },
                {
                    'statement': 'A magnetic field exerts force on a moving charge:',
                    'options': ['Always parallel to velocity', 'Always perpendicular to velocity', 'In the direction of velocity', 'Opposite to velocity'],
                    'correct': 2,
                },
                {
                    'statement': 'The direction of induced current is given by:',
                    'options': ['Lenz\'s law', 'Ohm\'s law', 'Faraday\'s law', 'Ampere\'s law'],
                    'correct': 1,
                },
                {
                    'statement': 'Capacitance of a parallel plate capacitor is proportional to:',
                    'options': ['A/d', 'Ad', 'd/A', 'A²/d²'],
                    'correct': 1,
                },
            ],
            'Optics': [
                {
                    'statement': 'Refractive index of a medium is defined as:',
                    'options': ['c/v', 'v/c', 'c-v', 'c+v'],
                    'correct': 1,
                },
                {
                    'statement': 'The focal length of a concave mirror is:',
                    'options': ['Positive', 'Negative', 'Zero', 'Infinity'],
                    'correct': 1,
                },
                {
                    'statement': 'According to Snell\'s law: n₁sin(θ₁) = n₂sin(θ₂), where θ is:',
                    'options': ['Angle of incidence/refraction', 'Angle between mirrors', 'Angle of lens', 'Polarization angle'],
                    'correct': 1,
                },
                {
                    'statement': 'The power of a lens is inversely proportional to:',
                    'options': ['Focal length', 'Radius of curvature', 'Wavelength', 'Frequency'],
                    'correct': 1,
                },
                {
                    'statement': 'Young\'s double slit experiment demonstrates:',
                    'options': ['Wave nature of light', 'Particle nature of light', 'Refraction of light', 'Dispersion of light'],
                    'correct': 1,
                },
            ],
            'Modern Physics': [
                {
                    'statement': 'Einstein\'s mass-energy relation is:',
                    'options': ['E = mc²', 'E = mgh', 'E = ½mv²', 'E = hf'],
                    'correct': 1,
                },
                {
                    'statement': 'Planck\'s constant h equals approximately:',
                    'options': ['6.63 × 10⁻³⁴ J·s', '3 × 10⁸ m/s', '9.8 m/s²', '1.6 × 10⁻¹⁹ C'],
                    'correct': 1,
                },
                {
                    'statement': 'The photoelectric effect proves:',
                    'options': ['Light has particle nature', 'Light has wave nature', 'Electrons are waves', 'Relativity theory'],
                    'correct': 1,
                },
                {
                    'statement': 'Bohr\'s model is valid for:',
                    'options': ['Hydrogen-like atoms', 'All atoms', 'Multi-electron atoms', 'Molecules'],
                    'correct': 1,
                },
                {
                    'statement': 'The uncertainty principle states that:',
                    'options': ['Δx·Δp ≥ h/4π', 'Δx·Δp = 0', 'Δx + Δp = constant', 'Δx = Δp'],
                    'correct': 1,
                },
            ],
        },
        'Chemistry': {
            'Organic Chemistry': [
                {
                    'statement': 'The general formula for alkanes is:',
                    'options': ['CₙH₂ₙ₊₂', 'CₙH₂ₙ', 'CₙH₂ₙ₋₂', 'CₙHₙ'],
                    'correct': 1,
                },
                {
                    'statement': 'Which functional group is present in alcohols?',
                    'options': ['-OH', '-CHO', '-COOH', '-NH₂'],
                    'correct': 1,
                },
                {
                    'statement': 'Carboxylic acids have the functional group:',
                    'options': ['-COOH', '-CHO', '-COO-', '-COH'],
                    'correct': 1,
                },
                {
                    'statement': 'Esterification is a reaction between:',
                    'options': ['Alcohol and Carboxylic acid', 'Two alcohols', 'Two carboxylic acids', 'Alcohol and aldehyde'],
                    'correct': 1,
                },
                {
                    'statement': 'Which compound is aromatic?',
                    'options': ['Benzene', 'Propane', 'Ethene', 'Butadiene'],
                    'correct': 1,
                },
            ],
            'Inorganic Chemistry': [
                {
                    'statement': 'The periodic table is arranged by:',
                    'options': ['Atomic number', 'Atomic mass', 'Electron configuration', 'Oxidation state'],
                    'correct': 1,
                },
                {
                    'statement': 'Which element is a metalloid?',
                    'options': ['Silicon', 'Sodium', 'Sulfur', 'Silver'],
                    'correct': 1,
                },
                {
                    'statement': 'Valence electrons determine:',
                    'options': ['Chemical properties', 'Atomic mass', 'Radioactivity', 'Density'],
                    'correct': 1,
                },
                {
                    'statement': 'A transition metal is characterized by:',
                    'options': ['Incomplete d-orbital', 'Complete s-orbital', 'No p-orbital', 'Single oxidation state'],
                    'correct': 1,
                },
                {
                    'statement': 'The oxidation state of oxygen in H₂O₂ is:',
                    'options': ['-1', '-2', '0', '+2'],
                    'correct': 1,
                },
            ],
            'Physical Chemistry': [
                {
                    'statement': 'The rate of reaction depends on:',
                    'options': ['Temperature, Concentration, Catalyst', 'Only temperature', 'Only pressure', 'Only concentration'],
                    'correct': 1,
                },
                {
                    'statement': 'pH of a neutral solution is:',
                    'options': ['7', '0', '14', '1'],
                    'correct': 1,
                },
                {
                    'statement': 'Gibbs free energy change (ΔG) determines:',
                    'options': ['Spontaneity of reaction', 'Rate of reaction', 'Equilibrium constant only', 'Temperature of reaction'],
                    'correct': 1,
                },
                {
                    'statement': 'Electronegativity increases across a period:',
                    'options': ['Left to right', 'Right to left', 'Top to bottom', 'Bottom to top'],
                    'correct': 1,
                },
                {
                    'statement': 'The equilibrium constant K depends on:',
                    'options': ['Temperature', 'Pressure', 'Concentration', 'Catalyst'],
                    'correct': 1,
                },
            ],
        },
        'Computer Science': {
            'Data Structures': [
                {
                    'statement': 'Time complexity of binary search is:',
                    'options': ['O(log n)', 'O(n)', 'O(n²)', 'O(n log n)'],
                    'correct': 1,
                },
                {
                    'statement': 'Space complexity of a stack is:',
                    'options': ['O(n)', 'O(1)', 'O(log n)', 'O(n²)'],
                    'correct': 1,
                },
                {
                    'statement': 'In a linked list, insertion at the beginning takes:',
                    'options': ['O(1)', 'O(n)', 'O(n log n)', 'O(log n)'],
                    'correct': 1,
                },
                {
                    'statement': 'Height of a balanced binary tree with n nodes is:',
                    'options': ['O(log n)', 'O(n)', 'O(n²)', 'O(1)'],
                    'correct': 1,
                },
                {
                    'statement': 'Hash table average case lookup is:',
                    'options': ['O(1)', 'O(log n)', 'O(n)', 'O(n²)'],
                    'correct': 1,
                },
            ],
            'Algorithms': [
                {
                    'statement': 'Which sorting algorithm has O(n log n) worst case?',
                    'options': ['Merge Sort', 'Bubble Sort', 'Insertion Sort', 'Selection Sort'],
                    'correct': 1,
                },
                {
                    'statement': 'Dynamic programming is useful for problems with:',
                    'options': ['Overlapping subproblems', 'Linear structure', 'Single solution', 'No constraints'],
                    'correct': 1,
                },
                {
                    'statement': 'Greedy algorithm works best for:',
                    'options': ['Activity selection problem', 'Knapsack problem', 'TSP', 'Graph coloring'],
                    'correct': 1,
                },
                {
                    'statement': 'Dijkstra\'s algorithm finds:',
                    'options': ['Shortest path', 'Longest path', 'Minimum spanning tree', 'Topological sort'],
                    'correct': 1,
                },
                {
                    'statement': 'Time complexity of quicksort average case is:',
                    'options': ['O(n log n)', 'O(n)', 'O(n²)', 'O(log n)'],
                    'correct': 1,
                },
            ],
            'Databases': [
                {
                    'statement': 'SQL query to get unique values is:',
                    'options': ['SELECT DISTINCT', 'SELECT UNIQUE', 'SELECT ALL', 'SELECT DIFFERENT'],
                    'correct': 1,
                },
                {
                    'statement': 'Primary key constraint ensures:',
                    'options': ['Uniqueness and NOT NULL', 'Only uniqueness', 'Only NOT NULL', 'Referential integrity'],
                    'correct': 1,
                },
                {
                    'statement': 'Third normal form (3NF) requires removal of:',
                    'options': ['Transitive dependencies', 'Partial dependencies', 'Repeating groups', 'Atomic values'],
                    'correct': 1,
                },
                {
                    'statement': 'ACID properties in databases stand for:',
                    'options': ['Atomicity, Consistency, Isolation, Durability', 'All, Check, Insert, Delete', 'Authorization, Confidentiality, Integrity, Delivery', 'Access, Control, Input, Data'],
                    'correct': 1,
                },
                {
                    'statement': 'Index on a column helps in:',
                    'options': ['Faster query execution', 'Saving space', 'Reducing memory', 'Decreasing complexity'],
                    'correct': 1,
                },
            ],
            'Operating Systems': [
                {
                    'statement': 'Context switching is done by:',
                    'options': ['CPU scheduler', 'Memory manager', 'Compiler', 'Loader'],
                    'correct': 1,
                },
                {
                    'statement': 'Deadlock occurs when:',
                    'options': ['Mutual exclusion, hold and wait, no preemption, circular wait', 'Process is blocked', 'CPU is busy', 'Memory is full'],
                    'correct': 1,
                },
                {
                    'statement': 'Page replacement algorithm FIFO can cause:',
                    'options': ['Belady\'s Anomaly', 'Deadlock', 'Thrashing', 'Starvation'],
                    'correct': 1,
                },
                {
                    'statement': 'Semaphore is used for:',
                    'options': ['Process synchronization', 'Memory allocation', 'File management', 'Device control'],
                    'correct': 1,
                },
                {
                    'statement': 'Virtual memory allows:',
                    'options': ['Using disk as extension of RAM', 'Faster CPU', 'Better security', 'Parallel processing'],
                    'correct': 1,
                },
            ],
        },
        'English Literature': {
            'Shakespeare': [
                {
                    'statement': 'In "Hamlet," the protagonist is the Prince of:',
                    'options': ['Denmark', 'England', 'France', 'Scotland'],
                    'correct': 1,
                },
                {
                    'statement': '"To be or not to be" is a soliloquy from:',
                    'options': ['Hamlet', 'Macbeth', 'Othello', 'King Lear'],
                    'correct': 1,
                },
                {
                    'statement': 'In "Romeo and Juliet," both main characters belong to:',
                    'options': ['Feuding families', 'Different countries', 'Different religions', 'Different social classes'],
                    'correct': 1,
                },
                {
                    'statement': '"Fair is foul, and foul is fair" appears in:',
                    'options': ['Macbeth', 'A Midsummer Night\'s Dream', 'The Tempest', 'Twelfth Night'],
                    'correct': 1,
                },
                {
                    'statement': 'The setting of "A Midsummer Night\'s Dream" is primarily:',
                    'options': ['An enchanted forest', 'A city', 'A castle', 'A village'],
                    'correct': 1,
                },
            ],
            'Modern Fiction': [
                {
                    'statement': 'George Orwell\'s "1984" depicts a:',
                    'options': ['Totalitarian state', 'Democratic society', 'Utopian world', 'Post-apocalyptic world'],
                    'correct': 1,
                },
                {
                    'statement': '"The Great Gatsby" is set in the:',
                    'options': ['1920s', '1930s', '1910s', '1940s'],
                    'correct': 1,
                },
                {
                    'statement': 'The protagonist of "To Kill a Mockingbird" is:',
                    'options': ['Scout Finch', 'Atticus Finch', 'Jem Finch', 'Boo Radley'],
                    'correct': 1,
                },
                {
                    'statement': '"The Catcher in the Rye" protagonist is:',
                    'options': ['Holden Caulfield', 'Phineas Grangerford', 'Sally Hayes', 'D.B. Doughlas'],
                    'correct': 1,
                },
                {
                    'statement': 'In "Pride and Prejudice," Elizabeth Bennet initially:',
                    'options': ['Dislikes Mr. Darcy', 'Admires Mr. Darcy', 'Is indifferent to him', 'Loves Mr. Darcy'],
                    'correct': 1,
                },
            ],
            'Poetry': [
                {
                    'statement': 'A rhyme scheme is:',
                    'options': ['Pattern of rhyming end words', 'Type of meter', 'Poetic device using repetition', 'Form of alliteration'],
                    'correct': 1,
                },
                {
                    'statement': 'Iambic pentameter has:',
                    'options': ['10 syllables per line', '8 syllables per line', '12 syllables per line', '5 syllables per line'],
                    'correct': 1,
                },
                {
                    'statement': 'Metaphor is a figure of speech that:',
                    'options': ['Compares two things without using "like" or "as"', 'Uses "like" or "as"', 'Exaggerates for effect', 'Repeats words for emphasis'],
                    'correct': 1,
                },
                {
                    'statement': 'In "The Road Not Taken," the speaker chooses:',
                    'options': ['The road less traveled by', 'The most traveled road', 'Neither road', 'Both roads'],
                    'correct': 1,
                },
                {
                    'statement': 'Alliteration is the repetition of:',
                    'options': ['Initial consonant sounds', 'Vowel sounds', 'Syllables', 'Whole words'],
                    'correct': 1,
                },
            ],
        },
    }

    def handle(self, *args, **options):
        self.stdout.write('Starting to seed JEE-level questions...')

        question_count = 0
        quiz_count = 0

        # Map difficulty levels to chapter/subject patterns
        difficulty_map = {
            'Algebra': 6,
            'Calculus': 7,
            'Geometry': 5,
            'Statistics': 4,
            'Mechanics': 7,
            'Thermodynamics': 6,
            'Electromagnetism': 8,
            'Optics': 6,
            'Modern Physics': 9,
            'Organic Chemistry': 7,
            'Inorganic Chemistry': 5,
            'Physical Chemistry': 8,
            'Data Structures': 6,
            'Algorithms': 7,
            'Databases': 5,
            'Operating Systems': 6,
            'Shakespeare': 4,
            'Modern Fiction': 4,
            'Poetry': 5,
        }

        for quiz in Quiz.objects.all():
            # Delete existing questions if any
            quiz.questions.all().delete()

            chapter = quiz.chapter
            subject = chapter.subject

            # Get difficulty level for this chapter
            base_difficulty = difficulty_map.get(chapter.name, 5)

            # Get questions for this subject and chapter
            subject_questions = self.JEE_QUESTIONS.get(subject.name, {})
            chapter_questions = subject_questions.get(chapter.name, [])

            if not chapter_questions:
                # Use first available chapter questions as fallback
                for available_chapter, questions in subject_questions.items():
                    if questions:
                        chapter_questions = questions
                        break

            # Add up to 5 questions per quiz with varying difficulty
            for q_idx, q_data in enumerate(chapter_questions[:5]):
                # Vary difficulty slightly within the range
                difficulty = min(10, max(1, base_difficulty + (q_idx - 2)))
                
                Question.objects.create(
                    quiz=quiz,
                    chapter=chapter,
                    subject=subject,
                    question_statement=q_data['statement'],
                    option_1=q_data['options'][0],
                    option_2=q_data['options'][1],
                    option_3=q_data['options'][2],
                    option_4=q_data['options'][3],
                    correct_option=q_data['correct'],
                    difficulty_level=difficulty,
                    remarks=f"JEE-level question {q_idx + 1} for {chapter.name} (Difficulty: {difficulty}/10)",
                )
                question_count += 1

            quiz_count += 1

        self.stdout.write(
            self.style.SUCCESS(
                f'Created {question_count} JEE-level questions for {quiz_count} quizzes with difficulty levels'
            )
        )
