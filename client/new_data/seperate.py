def extract_q_and_a(input_file, q_output_file, a_output_file):
    """
    Extracts questions (Q) and answers (A) from a document and saves them into separate files.

    Args:
        input_file (str): Path to the input file containing the Q&A content.
        q_output_file (str): Path to the output file for saving questions.
        a_output_file (str): Path to the output file for saving answers.
    """
    try:
        with open(input_file, 'r', encoding='utf-8') as infile:
            lines = infile.readlines()

        questions = []
        answers = []

        for line in lines:
            line = line.strip()  # Remove leading and trailing whitespace
            if line.startswith('Q:'):
                questions.append(line[2:].strip())  # Extract the question text after 'Q:'
            elif line.startswith('A:'):
                answers.append(line[2:].strip())  # Extract the answer text after 'A:'

        # Write questions to the Q output file
        with open(q_output_file, 'w', encoding='utf-8') as qfile:
            qfile.write('\n'.join(questions))

        # Write answers to the A output file
        with open(a_output_file, 'w', encoding='utf-8') as afile:
            afile.write('\n'.join(answers))

        print(f"Questions and answers successfully extracted:\nQ file: {q_output_file}\nA file: {a_output_file}")

    except Exception as e:
        print(f"An error occurred: {e}")

# Example usage
input_path = 'qna_sample.txt'       # Replace with your input file path
q_output_path = 'questions.txt'      # Replace with desired Q output file path
a_output_path = 'answers.txt'        # Replace with desired A output file path

extract_q_and_a(input_path, q_output_path, a_output_path)
