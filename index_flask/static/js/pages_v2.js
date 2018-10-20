// stan 2018-10-18


jQuery( function($) {

  $('table').click(function(e) {
    var table_id = $(this).attr('id');

    var target = $(e.target);
    if ( target.is( "td" ) ) {
      var tr = target.parent('tr');
      var record_id = tr.data('record_id');
      target.css( "background-color", "LemonChiffon" );
      show_dialog(table_id, record_id);
    } // if
  });

  $('#triggersModalSubmit').on('click', function(event) {
    var url = window.location.href;
    var formData = $("#send_comments").serialize();
    console.log(formData);
    $.post(url, formData).done(function (data) {
      $('#triggersModal').modal('hide');

      var table = $('table#table1').DataTable();
      table.draw();
    });
  });

} );


function show_dialog(table_id, record_id) {
  var triggersModal = document.querySelectorAll("#triggersModal")[0];
  var modal_body = triggersModal.querySelectorAll(".modal-body")[0];
  modal_body.innerHTML = '';

  document.querySelectorAll(`.command.trigger.${table_id}`).forEach(function(entry) {
    var suit = entry.dataset.suit;
    var button = entry.dataset.button;
    var button_class = entry.dataset.button_class;

    modal_body.innerHTML += `
<form method="post">
  <div class="row">
    <div class="col-2">
      <button type="submit" class="btn ${button_class}">${button}</button>
    </div>
    <div class="col">
      <div>
        <label for="action" class="sr-only"></label>
        <input class="form-control" type="hidden" id="action" name="action" value="trigger">
      </div>
      <div>
        <label for="action" class="sr-only"></label>
        <input class="form-control" type="hidden" id="suit" name="suit" value="${suit}">
      </div>
      <div>
        <label for="action" class="sr-only"></label>
        <input class="form-control" type="hidden" id="table_id" name="table_id" value="${table_id}">
      </div>
      <div>
        <label for="record_id" class="sr-only"></label>
        <input class="form-control" type="hidden" id="record_id" name="record_id" value="${record_id}">
      </div>
      <div class="form-group">
        <label for="remarks" class="sr-only"></label>
        <input class="form-control" type="text" id="remarks" name="remarks" placeholder="Remarks (optional)">
      </div>
    </div>
  </div>
</form>
<hr />`;
  });

  document.querySelectorAll(`.command.comment.${table_id}`).forEach(function(entry) {
    var suit = entry.dataset.suit;
    var prompt = entry.dataset.prompt ? entry.dataset.prompt : "Comments";

    modal_body.innerHTML += `
<form method="post" id="send_comments">
  <div>
    <label for="action" class="sr-only"></label>
    <input class="form-control" type="hidden" id="action" name="action" value="comment">
  </div>
  <div>
    <label for="action" class="sr-only"></label>
    <input class="form-control" type="hidden" id="suit" name="suit" value="${suit}">
  </div>
  <div>
    <label for="action" class="sr-only"></label>
    <input class="form-control" type="hidden" id="table_id" name="table_id" value="${table_id}">
  </div>
  <div>
    <label for="record_id" class="sr-only"></label>
    <input class="form-control" type="hidden" id="record_id" name="record_id" value="${record_id}">
  </div>
  <div class="form-group">
    <label for="comment" class="col-form-label">${prompt}:</label>
    <textarea class="form-control" id="comments" name="comments"></textarea>
  </div>
</form>`;
  });

  $('#triggersModal').modal();
} // function
