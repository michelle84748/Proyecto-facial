// templatemo 467 easy profile

// PRELOADER

$(window).load(function(){
    $('.preloader').delay(1000).fadeOut("slow"); // set duration in brackets    
});

// HOME BACKGROUND SLIDESHOW
$(function(){
    jQuery(document).ready(function() {
		$('body').backstretch([
	 		 "images/fondo.jpg", 
	 		 "images/fondo2.jpg",
			 "images/fondo3.jpg"
	 			], 	{duration: 3200, fade: 1300});
		});
})
document.getElementById("btn-registrar").addEventListener("click", function() {
    // Aquí puedes hacer una llamada al backend, utilizando Fetch API o AJAX, para ejecutar el script
    fetch('/ejecutar_registro', { method: 'POST' })
        .then(response => {
            if (response.ok) {
                alert('El proceso de registro ha comenzado.');
            } else {
                alert('Error al iniciar el registro.');
            }
        })
        .catch(error => console.error('Error:', error));
});
