import paramiko

class ChatBot:
    def __init__(self):
        self.model = "gpt-3.5-turbo"
        self.temperature = 0.3
        self.messages = [{"role": "system", "content": "You are a helpful assistant."}]

    def send_message(self, message):
        self.messages.append({"role": "user", "content": message})
        response = openai.ChatCompletion.create(
            model=self.model,
            messages=self.messages,
            temperature=self.temperature
        )
        return response.choices[0].message.content

    def connect_to_vm(self, hostname, username, password):
        try:
            # Create an SSH client
            client = paramiko.SSHClient()

            # Automatically add the server's host key
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

            # Connect to the VM
            client.connect(hostname, username=username, password=password)

            print("Connected to VM!")

            # Execute a command on the VM
            stdin, stdout, stderr = client.exec_command('ls')
            print(stdout.read().decode())

            # Close the connection
            client.close()

        except Exception as e:
            print(f"Failed to connect to VM: {e}")

# Replace 'hostname', 'username', and 'password' with your actual values
bot = ChatBot()
bot.connect_to_vm('hostname', 'username', 'password')
