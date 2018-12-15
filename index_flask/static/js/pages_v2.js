// stan 2018-10-18


jQuery( function($) {

  $('table').click(function(e) {
    var table_id = $(this).attr('id');

    var target = $(e.target);
    if ( target.is("td") ) {
      target.css("background-color", "LemonChiffon");

      var tr = target.closest('tr');
      var record_id = tr.data('record_id');

      if ( event.getModifierState("Control") ) {
        var th = target.closest('table').find('th').eq(target.index());
        var column_name = th.attr('id');
        if ( column_name )
          show_dialog2(table_id, record_id, column_name, target.html());

      } else
        show_dialog(table_id, record_id);
    } // if
  });

  $('#triggersModalSubmit').on('click', function(event) {
    var url = window.location.href;
    var formData = $(".default_modal_form").serialize();
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
        <label for="suit" class="sr-only"></label>
        <input class="form-control" type="hidden" id="suit" name="suit" value="${suit}">
      </div>
      <div>
        <label for="table_id" class="sr-only"></label>
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
<form method="post" class="default_modal_form">
  <div>
    <label for="action" class="sr-only"></label>
    <input class="form-control" type="hidden" id="action" name="action" value="comment">
  </div>
  <div>
    <label for="suit" class="sr-only"></label>
    <input class="form-control" type="hidden" id="suit" name="suit" value="${suit}">
  </div>
  <div>
    <label for="table_id" class="sr-only"></label>
    <input class="form-control" type="hidden" id="table_id" name="table_id" value="${table_id}">
  </div>
  <div>
    <label for="record_id" class="sr-only"></label>
    <input class="form-control" type="hidden" id="record_id" name="record_id" value="${record_id}">
  </div>
  <div class="form-group">
    <label for="comments" class="col-form-label">${prompt}:</label>
    <textarea class="form-control" id="comments" name="comments"></textarea>
  </div>
</form>`;
  });

  $('button[type="submit"]', modal_body).on('click', function(e) {
    e.preventDefault();   // prevent default action

    var url = window.location.href;
    var formData = $(this).closest('form').serialize();
    console.log(formData);
    $.post(url, formData).done(function (data) {
      $(triggersModal).modal('hide');

      var table = $('table#table1').DataTable();
      table.draw();
    });
  });

  $(triggersModal).modal();
} // function


function show_dialog2(table_id, record_id, column_name, column_value) {
  var modal_body = triggersModal.querySelectorAll(".modal-body")[0];
  modal_body.innerHTML = `
<div>Old value: ${column_value}</div>
<form method="post" class="default_modal_form">
  <div>
    <label for="action" class="sr-only"></label>
    <input class="form-control" type="hidden" id="action" name="action" value="correction">
  </div>
  <div>
    <label for="table_id" class="sr-only"></label>
    <input class="form-control" type="hidden" id="table_id" name="table_id" value="${table_id}">
  </div>
  <div>
    <label for="record_id" class="sr-only"></label>
    <input class="form-control" type="hidden" id="record_id" name="record_id" value="${record_id}">
  </div>
  <div>
    <label for="column_name" class="sr-only"></label>
    <input class="form-control" type="hidden" id="column_name" name="column_name" value="${column_name}">
  </div>
  <div class="form-group">
    <label for="new_value" class="col-form-label">New value:</label>
    <input class="form-control" id="new_value" name="new_value" required>
  </div>
</form>`;

  $(triggersModal).modal();
} // function
