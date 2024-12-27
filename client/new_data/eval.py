def calculate_average_score(file_path):
    """
    Calculate the average score from a file with a specific format.

    Args:
        file_path (str): Path to the input text file.

    Returns:
        float: The average score.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()

        total_score = 0
        count = 0

        for line in lines:
            line = line.strip()
            if line.startswith('점수 :'):
                try:
                    score = int(line.split(':')[1].strip())
                    total_score += score
                    count += 1
                except ValueError:
                    print(f"Warning: Unable to parse score in line: {line}")

        if count == 0:
            return 0.0  # Avoid division by zero if no scores are found

        average_score = total_score / count
        return average_score

    except FileNotFoundError:
        print(f"Error: File not found at {file_path}")
        return 0.0
    except Exception as e:
        print(f"An error occurred: {e}")
        return 0.0

# Example usage
file_path = 'eval_gpt_rag.txt'  # Replace with the path to your file
average = calculate_average_score(file_path)
print(f"The average score is: {average}")
