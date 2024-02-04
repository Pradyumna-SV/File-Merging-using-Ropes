import json
import time
import matplotlib.pyplot as plt

class RopeNode:
    def __init__(self, text=""):
        self.left = None
        self.right = None
        self.text = text
        self.content=text
        self.length = len(text)
    def __add__(self, other):
        # Perform the concatenation
        result = RopeNode()
        result.left = self
        result.right = other
        result.text = self.text
        result.length = self.length
    def get_text(self):
        if self.left is None and self.right is None:
            return self.text

        left_text = self.left.get_text()
        right_text = self.right.get_text()

        return left_text + right_text
    def concatenate(self, other_node):
        new_node = RopeNode(self.content + other_node.content)
        new_node+other_node
        return new_node

    def split(self, position):
        if position <= 0 or position >= len(self.content):
            return None

        left_content = self.content[:position]
        right_content = self.content[position:]

        left_node = RopeNode(left_content)
        right_node = RopeNode(right_content)

        left_node.left = self.left
        left_node.right = right_node
        right_node.left = left_node
        right_node.right = self.right

        if self.left:
            self.left.right = left_node
        if self.right:
            self.right.left = right_node

        return left_node, right_node


class DataArchiver:
    def __init__(self):
        self.metadata = {}
        self.rope_data = {}
        self.file_path = "data.json"  # File path for saving and loading data

        # Load data from file if it exists
        self.load_data()

    def add_file(self, filename, content, metadata):
        rope_node = RopeNode(content)
        self.rope_data[filename] = rope_node
        self.metadata[filename] = metadata

        # Save data to file
        self.save_data()


    def get_file_content(self, filename):
        if filename in self.rope_data:
            rope_node = self.rope_data[filename]
            return rope_node.content
        return None

    def search_files(self, query):
        results = []
        parts = query.split(" ")
        if len(parts) == 3:
            attribute = parts[0]
            operator = parts[1]
            value = int(parts[2])  # Convert value to an integer

            for filename, metadata in self.metadata.items():
                if attribute in metadata:
                    attribute_value = int(metadata[attribute])  # Convert attribute value to an integer

                    if operator == ">" and attribute_value > value:
                        results.append(filename)
                    elif operator == ">=" and attribute_value >= value:
                        results.append(filename)
                    elif operator == "<" and attribute_value < value:
                        results.append(filename)
                    elif operator == "<=" and attribute_value <= value:
                        results.append(filename)
                    elif operator == "==" and attribute_value == value:
                        results.append(filename)
        return results


    def filter_files(self, attribute, value):
        results = []
        for filename, metadata in self.metadata.items():
            if attribute in metadata and metadata[attribute] == value:
                results.append(filename)
        return results

    def update_file(self, filename, new_content, new_metadata):
        if filename in self.rope_data:
            rope_node = self.rope_data[filename]
            rope_node.content = new_content
        self.metadata[filename] = new_metadata

    def get_file_metadata(self, filename):
        if filename in self.metadata:
            return self.metadata[filename]
        return None

    
    def merge_files(self, filename1, filename2, new_filename):
        if filename1 in self.rope_data and filename2 in self.rope_data:
            rope_node1 = self.rope_data[filename1]
            rope_node2 = self.rope_data[filename2]
            merged_node = rope_node1.concatenate(rope_node2)
            self.rope_data[new_filename] = merged_node
            self.metadata[new_filename] = {}

    def search_file_content(self, query):
        results = []
        query = query.lower()

        for filename, metadata in self.metadata.items():
            rope_node = self.rope_data.get(filename)
            if rope_node is not None:
                if query in rope_node.content.lower():
                    results.append(filename)

        return results

    def split_file_content(self, filename, position):
        if filename in self.rope_data:
            rope_node = self.rope_data[filename]
            left_node, right_node = rope_node.split(position)
            if left_node and right_node:
                left_filename = filename + "_split_left"
                right_filename = filename + "_split_right"
                self.rope_data[left_filename] = left_node
                self.rope_data[right_filename] = right_node
                self.metadata[left_filename] = self.metadata[filename].copy()
                self.metadata[right_filename] = self.metadata[filename].copy()
                return left_filename, right_filename
        return None, None
    

    def delete_file(self, filename):
        if filename in self.rope_data:
            del self.rope_data[filename]
            del self.metadata[filename]
            self.save_data()  # Save data to file after deleting a file
            return True
        return False

    def save_data(self):
        data = {
            "metadata": self.metadata,
            "rope_data": {filename: node.content for filename, node in self.rope_data.items()},
        }

        with open(self.file_path, "w") as file:
            json.dump(data, file)

    def load_data(self):
        try:
            with open(self.file_path, "r") as file:
                data = json.load(file)
                self.metadata = data.get("metadata", {})
                self.rope_data = {
                    filename: RopeNode(content) for filename, content in data.get("rope_data", {}).items()
                }
        except FileNotFoundError:
            pass


    def list_all_files(self):
        return list(self.rope_data.keys())




# Add more measurement functions for additional operations

# Create an instance of the DataArchiver class
data_archiver = DataArchiver()

# List of file sizes for the operations that involve file content
file_sizes = [100, 500, 1000]

# List to store the measured runtimes
runtimes = []


# Add more measurement functions for additional operations






def measure_update_file_runtime(data_archiver, filename, new_content, new_metadata):
    start_time = time.time()
    data_archiver.update_file(filename, new_content, new_metadata)
    end_time = time.time()
    return end_time - start_time



def measure_merge_files_runtime(data_archiver, filename1, filename2, new_filename):
    start_time = time.time()
    data_archiver.merge_files(filename1, filename2, new_filename)
    end_time = time.time()
    return end_time - start_time



# List of operation numbers and corresponding function names
operations = {
    1: ("Update File", measure_update_file_runtime),
    2: ("Merge Files", measure_merge_files_runtime)
}

# User input for selecting the operation
print("Select the operation:")
for operation_num, operation_name in operations.items():
    print(f"{operation_num}. {operation_name[0]}")

operation_num = int(input("Enter the operation number: "))

# Get the corresponding function for the selected operation
measure_function = operations.get(operation_num)[1]

# Measure the runtime for the selected operation
if measure_function:
    for size in file_sizes:
        runtime = measure_function(data_archiver, "filename", "content", {})
        runtimes.append(runtime)

# Plot the runtimes
plt.plot(file_sizes, runtimes, marker='o')
plt.xlabel("File Size")
plt.ylabel("Runtime (s)")
plt.title("Runtime Comparison")
plt.show()


