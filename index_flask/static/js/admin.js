// stan 2016-07-06


jQuery( function($) {


  /*** EVENTS ***/

  /* Extend table */

  $("input.user_group").click( function(event) {
    input = $(this);

    var id = input.data("id");
    var group = input.data("group");

    var data = {
      "id": id,
      "group": group,
      "status": input.prop('checked'),
    };

    $.ajax({
      type: "POST",
      dataType: "json",
      url: this.baseURI,
      data: data,
      async: false,
      success: function(data) {
        debug(data);
      },
      error: function(xhr, error, thrown) {
        debug(thrown);
      },
    });
  } );


} );
