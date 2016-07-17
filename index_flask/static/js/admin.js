// stan 2016-07-06


jQuery( function($) {


  /*** EVENTS ***/

  /* Action handler */

  $("span.for_action").click( function(event) {
    span = $(this);
    span1 = span[0];

    data = get_data(span1);

    $.post(this.baseURI, data, function(data) {
        debug(data);
    } );
  } );


  /* Action handler for inputs */

  $("input.for_action").click( function(event) {
    input = $(this);
    input1 = input[0];

    data = get_data(input1);
    data["checked"] = input.prop('checked')

    $.post(this.baseURI, data, function(data) {
        debug(data);
    } );
  } );


  /*** FUNCTIONS ***/

  function get_data(cls) {
    data = {}
    for (name in cls.attributes) {
      obj = cls.attributes[name];
      if ( typeof obj == "object" && obj.name.indexOf("data-") === 0 )
          data[obj.name.slice(5)] = obj.value
    } // for

    return data;
  } // get_data


} );
