document.getElementById('contactForm').addEventListener('submit', function(event) {
    event.preventDefault();

    var firstName = document.getElementById('first_name').value;
    var lastName = document.getElementById('last_name').value;
    var phone = document.getElementById('phone').value;
    var email = document.getElementById('email').value;
    var company = document.getElementById('company').value;
    var notes = document.getElementById('notes').value;
    var weburl = document.getElementById('weburl').value; // Added line for web URL

    // Updated vCard string to include the web URL
    var vCardString = `BEGIN:VCARD\nVERSION:3.0\nFN:${firstName} ${lastName}\nTEL:${phone}\nEMAIL:${email}\nORG:${company}\nURL:${weburl}\nNOTE:${notes}\nEND:VCARD`;

    // Assuming you have a QRCode library loaded to handle this
    QRCode.toDataURL(vCardString, function (err, url) {
        if (err) {
            console.error(err);
            // Handle the error case here
            return;
        }
        document.getElementById('qrcode').innerHTML = `<img src="${url}"/>`;
    });
});
