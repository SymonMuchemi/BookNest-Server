from fabric import Connection

ec2_host = "ubuntu@ec2-13-60-217-222.eu-north-1.compute.amazonaws.com"
key_file = "~/.ssh/booknest-key.pem"

# Connect to the EC2 instance
conn = Connection(host=ec2_host, connect_kwargs={"key_filename": key_file})

project_directory = "/BookNest-Server"
branch_name = "main"

with conn.cd(project_directory):
    result = conn.run(f"git pull origin {branch_name}")
    print(result.stdout)
