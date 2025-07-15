console.log("working fine");

$(document).on('submit', '#contact-form-ajax', function (e){
    e.preventDefault();
    console.log('Form submitted');

    let full_name = $('#full_name').val()
    let email = $('#email').val()
    let message = $('#message').val()

    console.log('Full Name:', full_name);
    console.log('Email:', email);
    console.log('Message:', message);

    $.ajax({
        url: '/ajax-contact-form',
        data: {
            'full_name': full_name,
            'email': email,
            'message': message
        },
        dataType: 'json',
        beforeSend: function(){
            console.log('Sending data to server...');
        },
        success: function(res){
            console.log('Data sent successfully');
            $('#contact-form-ajax').hide();
            $('#message-response').html('Your message has been sent successfully.').show();
        }
    })
});