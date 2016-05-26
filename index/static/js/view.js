// stan 2014-12-05


jQuery( function($) {


  /*** Startup ***/

  $(document).ready( function() {
    if (window.location.hash) {
      var hash = window.location.hash;
      window.location.hash = '';
//    apply_code(hash);
    }
  } );


  /*** EVENTS ***/

  /* Extend table */

  $(".extendtable").click( function(event) {
    debug(this.baseURI);
    debug($(this).data("offset"));
  } );


  /*** FUNCTIONS ***/


} );
