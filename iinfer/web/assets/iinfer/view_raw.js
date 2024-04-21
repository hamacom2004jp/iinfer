// RAW結果をモーダルダイアログに表示
view_raw_func = (title, result) => {
    result_modal = $(`#result_modal`);
    result_modal.find(`.modal-title`).text(title);
    result_modal.find(`.modal-body`).html(``);
    table = $(`<table class="table table-bordered table-hover table-sm"></table>`);
    table_head = $(`<thead class="table-dark bg-dark"></thead>`);
    table_body = $(`<tbody></tbody>`);
    table.append(table_head);
    table.append(table_body);
    result_modal.find(`.modal-body`).append(table);
    // list型の結果をテーブルに変換
    list2table = (data, table_head, table_body) => {
        $.each(data, (i, row) => {
            tr = $(`<tr></tr>`);
            if (typeof row === `string`){
                tr.append($(`<td>${row}</td>`));
            }
            else {
                $.each(row, (key, val) => {
                    if(i==0) {
                        table_head.append($(`<th scope="col">${key}</th>`));
                    }
                    tr.append($(`<td>${val}</td>`));
                });
            }
            table_body.append(tr);
        });
    }
    list2table(result, table_head, table_body);
    result_modal.modal(`show`);
}