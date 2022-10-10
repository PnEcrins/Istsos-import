$(document).ready(function () {
  var table = $("#import-table").DataTable({
    serverSide: true,
    processing: true,
    ajax: api_imports,
    pageLength: 10,
    columns: [
      { data: "id_import" },
      { data: "procedure.name_prc" },
      { data: "date_import" },
      { data: "file_name" },
      { data: "nb_row_inserted" },
      { data: "nb_row_total" },
    ],
  });
});
