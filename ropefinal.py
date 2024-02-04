import json
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


# Driver code
archiver = DataArchiver()

def print_header(text):
    print("=" * 40)
    print(text)
    print("=" * 40)

# Function to display the menu
def display_menu():
    print_header("Data Archiver Menu")
    print("1. Add a file")
    print("2. Retrieve file content")
    print("3. Retrieve file metadata")
    print("4. Search files based on metadata")
    print("5. Filter files based on metadata")
    print("6. Update a file")
    print("7. Merge files")
    print("8. Search for files based on content")
    print("9. Split file content")
    print("10. List all files")
    print("11. Delete a file")
    print("0. Exit")
    print_separator()


# Function to get user input as integer
def get_user_choice():
    while True:
        try:
            choice = int(input("Enter your choice (0-11): "))
            return choice
        except ValueError:
            print("Invalid input. Please enter a number.")

# Function to add a file
def add_file():
    filename = input("Enter filename: ")
    content = input("Enter file content: ")
    metadata = {}
    num_metadata = int(input("Enter the number of metadata attributes: "))
    for _ in range(num_metadata):
        attribute = input("Enter attribute name: ")
        value = input("Enter attribute value: ")
        metadata[attribute] = value
    archiver.add_file(filename, content, metadata)
    print("File added successfully.")

# Function to retrieve file content
def retrieve_file_content():
    filename = input("Enter filename: ")
    content = archiver.get_file_content(filename)
    if content:
        print("File content:")
        print(content)
    else:
        print("File not found.")

# Function to retrieve file metadata
def retrieve_file_metadata():
    filename = input("Enter filename: ")
    metadata = archiver.get_file_metadata(filename)
    if metadata:
        print("File metadata:")
        print(metadata)
    else:
        print("File not found.")

# Function to search files based on metadata
def search_files():
    query = input("Enter search query (e.g., size > 100): ")
    results = archiver.search_files(query)
    if results:
        print("Search results:")
        for result in results:
            print(result)
    else:
        print("No files found.")

# Function to filter files based on metadata
def filter_files():
    attribute = input("Enter attribute name: ")
    value = input("Enter attribute value: ")
    results = archiver.filter_files(attribute, value)
    if results:
        print("Filtered results:")
        for result in results:
            print(result)
    else:
        print("No files found.")

# Function to update a file
def update_file():
    filename = input("Enter filename: ")
    new_content = input("Enter new file content: ")
    new_metadata = {}
    num_metadata = int(input("Enter the number of metadata attributes: "))
    for _ in range(num_metadata):
        attribute = input("Enter attribute name: ")
        value = input("Enter attribute value: ")
        new_metadata[attribute] = value
    archiver.update_file(filename, new_content, new_metadata)
    print("File updated successfully.")


# Function to merge files
def merge_files():
    filename1 = input("Enter filename 1: ")
    filename2 = input("Enter filename 2: ")
    new_filename = input("Enter the name for the merged file: ")
    archiver.merge_files(filename1, filename2, new_filename)
    print("Files merged successfully.")

# Function to search for files based on content
def search_file_content():
    query = input("Enter search query: ")
    results = archiver.search_file_content(query)
    if results:
        print("Search results:")
        for result in results:
            print(result)
    else:
        print("No files found.")

# Function to split file content
def split_file_content():
    filename = input("Enter filename: ")
    position = int(input("Enter the split position: "))
    left_filename, right_filename = archiver.split_file_content(filename, position)
    if left_filename and right_filename:
        left_content = archiver.get_file_content(left_filename)
        right_content = archiver.get_file_content(right_filename)
        print("Two new files with the split content are:")
        print("Left file content:")
        print(left_content)
        print("Right file content:")
        print(right_content)
    else:
        print("Splitting failed.")

# Function to delete a file
def delete_file():
    filename = input("Enter filename: ")
    deleted = archiver.delete_file(filename)
    if deleted:
        print(f"File '{filename}' has been deleted.")
    else:
        print(f"File '{filename}' not found.")

# Function to list all files
def list_all_files():
    all_files = archiver.list_all_files()
    print("All files:")
    for file in all_files:
        print(file)

def print_separator():
    print("-" * 50)

# Main program
# Main program
while True:
    display_menu()
    choice = get_user_choice()

    if choice == 0:
        print("Exiting...")
        break
    elif choice == 1:
        add_file()
    elif choice == 2:
        retrieve_file_content()
    elif choice == 3:
        retrieve_file_metadata()
    elif choice == 4:
        search_files()
    elif choice == 5:
        filter_files()
    elif choice == 6:
        update_file()
    elif choice == 7:
        merge_files()
    elif choice == 8:
        search_file_content()
    elif choice == 9:
        split_file_content()
    elif choice == 10:
        list_all_files()
    elif choice == 11:
        delete_file()
    else:
        print("Invalid choice. Please enter a number between 0 and 13.")

    # Ask if the user wants to continue
    print()
    user_input = input("Do you want to continue? (y/n): ")
    if user_input.lower() != "y":
        print("Exiting...")
        break