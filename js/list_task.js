// Execute the 'onLoad' function after the page has finished loading
$(onLoad)

function onLoad() {
  // Filtrer par le nom de tâche
  $("filter-task-by-name").on("input",filterRowsByName)
}

function filterRowsByName() {
  const table = document.getElementById('taches');
  const names = table.querySelectorAll('th');





  // 1. Get the value of the input `filter-friends`
  // Look for `value` or `val` in jQuery
  var filter_value = $("#filter-task-by-name").val().toLowerCase();
  // 2. Hide all rows whose name do not contain the string `filter`.
  // Hint: use $().filter() to filter elements matching a predicate, and
  // $().hide() to hide elements from the page
  $("#taches tbody tr").show();
  $("#taches tbody tr").filter(function () {
    return $( this ).attr( "data-name" ).indexOf(filter_friend_value) === -1;
  }).hide();
}