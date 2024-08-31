document.addEventListener('DOMContentLoaded', function() {
    console.log('DOMContentLoaded event triggered');
    var video = document.getElementById('video-bg');
    var content = document.getElementById('content');

    setTimeout(function() {
        content.style.display = 'block';
    }, 3000); // Display content after 3 seconds (3000 milliseconds)
});
