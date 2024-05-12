from flask import Flask, render_template, request, redirect, url_for, flash
import docker
import os
app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Create a Docker client
docker_client = docker.from_env()

@app.route('/')
def index():
    # Fetch container data
    containers = []
    try:
        docker_containers = docker_client.containers.list(all=True)
        for container in docker_containers:
            containers.append({
                "id": container.short_id,
                "name": container.name,
                "status": container.status
            })
    except docker.errors.APIError as e:
        error_message = f"Failed to fetch container data: {str(e)}"
        return render_template('error.html', error_message=error_message)

    # Fetch image data
    images = []
    try:
        docker_images = docker_client.images.list()
        for image in docker_images:
            images.append({
                "id": image.short_id,
                "repository": image.tags[0] if image.tags else "",
                "created": image.attrs['Created'],
                "size": image.attrs['Size']
            })
    except docker.errors.APIError as e:
        error_message = f"Failed to fetch image data: {str(e)}"
        return render_template('error.html', error_message=error_message)

    return render_template('index.html', containers=containers, images=images)

@app.route('/create_dockerfile_form')
def create_dockerfile_form():
    return render_template('create_dockerfile_form.html')

@app.route('/generate_dockerfile', methods=['POST'])
def generate_dockerfile():
    image_name = request.form.get('image_name')
    workdir = request.form.get('workdir')
    cmd = request.form.get('cmd')
    entrypoint = request.form.get('entrypoint')
    env = request.form.get('env')
    copy = request.form.get('copy')
    expose = request.form.get('expose')

    if image_name:
        try:
            # Create the Dockerfile content
            dockerfile_content = f"FROM {image_name}\n"

            # Add additional options to the Dockerfile
            if workdir:
                dockerfile_content += f"WORKDIR {workdir}\n"
            if cmd:
                dockerfile_content += f"CMD {cmd}\n"
            if entrypoint:
                dockerfile_content += f"ENTRYPOINT {entrypoint}\n"
            if env:
                env_vars = env.split(',')
                for env_var in env_vars:
                    dockerfile_content += f"ENV {env_var}\n"
            if copy:
                copy_args = copy.split(' ')
                if len(copy_args) == 2:
                    dockerfile_content += f"COPY {copy_args[0]} {copy_args[1]}\n"
            if expose:
                exposed_ports = expose.split(',')
                for port in exposed_ports:
                    dockerfile_content += f"EXPOSE {port}\n"

            # Define the Dockerfile path
            dockerfile_path = 'Dockerfile_generated'

            # Save the Dockerfile content to a file
            with open(dockerfile_path, 'w') as dockerfile:
                dockerfile.write(dockerfile_content)

            flash('Dockerfile created successfully!', 'success')
        except Exception as e:
            flash(f'Failed to create Dockerfile: {str(e)}', 'danger')
    else:
        flash('Image name is required.', 'danger')

    return redirect(url_for('create_dockerfile_form'))

@app.route('/open_terminal')
def open_terminal():
    try:
        os.system('start cmd')  # This command opens the Windows command prompt (terminal)
        flash('Terminal opened successfully!', 'success')
    except Exception as e:
        flash(f'Failed to open terminal: {str(e)}', 'danger')
    return redirect(url_for('index'))

@app.route('/create_container_form')
def create_container_form():
    return render_template('create_container_form.html')

@app.route('/create_container', methods=['POST'])
def create_container():
    image_id = request.form.get('image_id')

    if image_id:
        try:
            # Create a container from the specified image ID
            docker_client.containers.create(image=image_id)
            flash('Container created successfully!', 'success')
        except Exception as e:
            flash(f'Failed to create container: {str(e)}', 'danger')
    else:
        flash('Image ID is required.', 'danger')

    return redirect(url_for('create_container_form'))

@app.route('/create_image_form')
def create_image_form():
    return render_template('create_image_form.html')
@app.route('/create_image', methods=['POST'])
def create_image():
    container_id = request.form.get('container_id')

    if container_id:
        try:
            container = docker_client.containers.get(container_id)
            container.commit(repository='', tag='created_image')
            flash('Image created from container successfully!', 'success')
        except Exception as e:
            flash(f'Failed to create image from container: {str(e)}', 'danger')
    else:
        flash('Container ID is required.', 'danger')

    return redirect(url_for('create_image_form'))

@app.route('/stop_container_form')
def stop_container_form():
    return render_template('stop_container_form.html')

@app.route('/stop_container', methods=['POST'])
def stop_container():
    container_id = request.form.get('container_id')

    if container_id:
        try:
            container = docker_client.containers.get(container_id)
            container.stop()
            flash('Container stopped successfully!', 'success')
        except Exception as e:
            flash(f'Failed to stop container: {str(e)}', 'danger')
    else:
        flash('Container ID is required.', 'danger')

    return redirect(url_for('stop_container_form'))
@app.route('/aboutus')
def about():
    return render_template('aboutus.html')


if __name__ == '__main__':
    app.run(debug=True, port=8080)
