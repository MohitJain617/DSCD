import subprocess

# Run the client process and capture the output
client_process = subprocess.Popen(['python3', 'client.py'], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)

# Send input to the subprocess and read its output
client_inputs = [ 'w\nu\nselfassigneduuid1\nfile1\nThis is content for File 1.\n',
                	'r\nselfassigneduuid1\n'
					'w\nu\nselfassigneduuid2\nfile2\nThis is content for File 2.\n',
					'r\nselfassigneduuid2\n',
					'd\nselfassigneduuid1\n',
					'r\nselfassigneduuid1\n',
					'q\n']

# Send multiple inputs to the subprocess and accumulate its output
output = ""
errors = ""
client_inputs = ['w\n', 'u\n', 'selfassigneduuid1\n', 'file1\n', 'This is content for File 1.\n', 'q\n']
client_inputs = ['que\n',]
for input_data in client_inputs:
	print("Sending input to client: ", input_data)
	# Send input to the subprocess
	client_process.stdin.write(input_data)
	client_process.stdin.flush()
	print("input sent")

    # Read output from the subprocess
	output += client_process.stdout.read()
	# errors += client_process.stderr.read()
	print("Output decoded")

# Close the subprocess's input stream
client_process.stdin.close()

return_code = client_process.wait()

if(return_code != 0):
	print("Client process exited with error code: ", return_code)
	print("Client process output: ")
	print(output)
	print("Client process errors: ", errors)
	exit(1)
else:
	print("Success!")
	print("Client process output: ")
	print(output)


 
 
