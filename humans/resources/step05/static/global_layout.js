$(function() {

    function get_updates () {
        $.getJSON('/updates.json', function(data) {
            var target = $('#sidebar ul');
            target.empty();
            $.each(data, function (key, val) {
                target.append('<li>Update #' + val + '</li>');
            });
        });
    }

    $('#sidebar a').click(function () {
        get_updates();
    });

    get_updates();
});