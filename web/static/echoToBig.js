document.addEventListener('DOMContentLoaded', function() {

    function echoToBig() {
        var input = document.getElementById('input');
        var output = document.getElementById('output');
        output.innerHTML = input.value;
    }

    var input = document.getElementById('input');
    input.addEventListener('input', echoToBig);

});