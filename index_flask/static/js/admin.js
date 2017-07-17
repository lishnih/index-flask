// stan 2016-07-06


jQuery( function($) {


  /*** EVENTS ***/

  /* Action handler */

  $("span.for_action").click( function(event) {
    span = $(this);

    tr = span.closest("tr");

    $.post(this.baseURI, span.data(), function(data) {
        debug(data);

        if ( data.result == 'accepted' )
          tr.remove();
    } );
  } );


  /* Action handler for inputs */

  $("input.for_action").click( function(event) {
    input = $(this);

    data = input.data();
    data["checked"] = input.prop('checked')

    $.post(this.baseURI, input.data(), function(data) {
        debug(data);
    } );
  } );


} );
