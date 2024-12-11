document.addEventListener("DOMContentLoaded", function() {
    const form = document.getElementById("uploadForm");

    // Listen for form submission
    form.addEventListener("submit", function(event) {
        event.preventDefault();

            Swal.fire({
                title: 'Success!',
                text: 'Your file was uploaded successfully!',
                icon: 'success',
                confirmButtonText: 'OK'
            });

        setTimeout(function() {
            form.submit();
        }, 2000);
    });
});
