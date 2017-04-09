$(document).ready(function() {

    $('#btnflushdata').click( function() {
        $.ajax({
            type: 'POST',
            url: '/api/v1.0/flush_status',
            success: function(data) {
                var result = (data.result);
                if (result) {
                    window.location.href="/"
                } else {
                    alert("Error: Cannot flush services status !")
                }
            },
            error: function() {
                alert("Something went wrong");
            }
        });
        return false; // to stop link
    });
});