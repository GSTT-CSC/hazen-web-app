{% extends "base.html" %}
{% import "bootstrap5/form.html" as wtf %}

{% block title %}{{title}}{% endblock %}

{% block app_content %}
<style>
    .scrollspy-example {
        position: relative;
        /*height: 200px;*/
        overflow: auto;
    }
</style>


<!-- FILE UPLOAD -->
<div class="row"> <!-- col-md-4 col-lg-3 pb-3 -->
    <div class="col">
        <h3 class="text-center pt-2">Upload new files</h3>
        <!-- File upload form -->
        {{ super() }}
        {{ dropzone.load_css() }}
        {{ dropzone.style('border: 5px dashed gray; margin: auto; min-height: 100px; max-width: 700px') }}
        {{ dropzone.create(action=url_for('main.workbench'))}}
        {{ dropzone.load_js() }}
        {{ dropzone.config(reload='main.workbench', id='uploader') }}

        <!-- Folder upload form -->
        <div id="file-upload-container">
            <form id="upload-folder-form" method="POST" enctype="multipart/form-data">
                <input type="file" name="folder" id="folder" webkitdirectory>
                <button type="submit">Upload</button>
            </form>
        </div>

        <!-- Reload button -->
        <div class="text-center">
            <button onClick="window.location.reload()" id="upload" class="btn btn-primary">Upload</button>
        </div>

        <!-- File selection form -->
        <div class="row">
            {% if upload_form %}
                {{ wtf.render_form(upload_form) }}
            {% endif %}
        </div>
    </div>
</div>

<!-- FOLDER UPLOAD SCRIPT -->
<script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>
<script>
    $('#upload-folder-form').on('submit', function (e) {
        e.preventDefault();
        const folderInput = document.getElementById('folder');
        const formData = new FormData();
        for (const file of folderInput.files) {
            formData.append('files', file);
        }
        fetch('/upload_folder', {
            method: 'POST',
            body: formData
        }).then(response => {
            console.log(response);
            // Reload the webpage to display the updated list of files
            location.href = "{{ url_for('main.workbench') }}";
        });
    });
</script>


<form method="POST" action={{ url_for('main.workbench') }}>
    <div class="col">
        <!-- Task list Scrollspy -->
        <div id="scrollspy1" style="background-color