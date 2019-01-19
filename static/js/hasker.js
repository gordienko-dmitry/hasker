$(document).ready(function () {

    $('#search-field-js').focus(function () {
        $('#search-btn-js').show();
    });

    $('#search-field-js').blur(function () {
        $('#search-btn-js').hide();
    });

    $('body').on("click", ".click-page",function (event) {
        $.get(window.location.pathname + '?page=' + $(this).text(), function (data) {
            $('#middle-context').html(data);
        })
        //window.location.pathname
    });

    $('#photo').bind("click", function (event) {
        $('#avatar').trigger('click');
    });
    $('#avatar').change(function (evt) {
        if (this.files && this.files[0]) {
            var reader = new FileReader();
            reader.onload = function (e) {
                $('#photo').attr('src', e.target.result);
            }
            reader.readAsDataURL(this.files[0]);
        }
    });

    // vote
    $('body').on('click', '.up-click', function (event) {
        event.preventDefault();
        var name = this.name;
        $.ajax({
            type: 'POST',
            url: '/vote',
            data: {
                'csrfmiddlewaretoken': window.CSRF_TOKEN,
                'entity': 'a', 'id': this.name, 'up': true
            },
            success: function (data) {
                $('#answer' + name).html(data);
            }
        });
    });

    // vote
    $('body').on('click', '.down-click', function (event) {
        event.preventDefault();
        var name = this.name;
        $.ajax({
            type: 'POST',
            url: '/vote',
            data: {
                'csrfmiddlewaretoken': window.CSRF_TOKEN,
                'entity': 'a', 'id': this.name, 'up': false
            },
            success: function (data) {
                $('#answer' + name).html(data);
            }
        });
    });

    // vote
    $('body').on('click', '.up-click-q', function (event) {
        event.preventDefault();
        var name = this.name;
        $.ajax({
            type: 'POST',
            url: '/vote',
            data: {
                'csrfmiddlewaretoken': window.CSRF_TOKEN,
                'entity': 'q', 'up': true, 'id': name
            },
            success: function (data) {
                $('#question').html(data);
            }
        });
    });

    // vote
    $('body').on('click', '.down-click-q', function (event) {
        event.preventDefault();
        var name = this.name;
        $.ajax({
            type: 'POST',
            url: '/vote',
            data: {
                'csrfmiddlewaretoken': window.CSRF_TOKEN,
                'entity': 'q', 'up': false, 'id': name
            },
            success: function (data) {
                $('#question').html(data);
            }
        });
    });

    //alert(window.location.pathname);

    if (window.location.pathname == "/ask") {
        $.fn.inputTags.defaults["errors"] = {
            empty: 'Attention',
            minLength: 'Attention',
            maxLength: 'Attention, too much tags, you may use %s',
            max: 'Attention, too much tags, you may use %s',
            email: 'Attention',
            exists: 'Attention, double tag !',
            autocomplete_only: 'Attention, not from list.',
            timeout: 8000
        };
        var tags = $('#tags').inputTags({
            tags: [],
            max: 3,
            create: function () {
                //alert('create');
            }
        });
    }
    ;


    //$('#tags').on('input', function () {
    //    $get('tags')
    //});

});