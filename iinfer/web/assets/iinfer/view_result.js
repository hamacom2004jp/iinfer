// 実行結果をモーダルダイアログに表示
view_result_func = (title, result) => {
    result_modal = $(`#result_modal`);
    result_modal.find(`.modal-title`).text(title);
    result_modal.find(`.modal-body`).html(``);
    mk_table_func = () => {
        table = $(`<table class="table table-bordered table-hover table-sm"></table>`);
        table_head = $(`<thead class="table-dark bg-dark"></thead>`);
        table_body = $(`<tbody></tbody>`);
        table.append(table_head);
        table.append(table_body);
        return table;
    }
    result_modal.find(`.modal-body`).append(mk_table_func());
    // list型の結果をテーブルに変換
    list2table = (data, table_head, table_body) => {
        $.each(data, (i, row) => {
            if(row[`success`] && typeof row[`success`] == "object" && !Array.isArray(row[`success`])){
                dict2table(row[`success`], i==0?table_head:null, table_body, row[`output_image`]);
                return;
            }
            if(typeof row == `string` || row instanceof String){
                tr = $(`<tr></tr>`);
                table_body.append(tr);
                tr.append($(`<td>${row}</td>`));
                return;
            }
            tr = $(`<tr></tr>`);
            table_body.append(tr);
            $.each(row, (key, val) => {
                if(i==0) {
                    table_head.append($(`<th scope="col">${key}</th>`));
                }
                if(val && val[`success`] && Array.isArray(val[`success`])){
                    tbl = mk_table_func()
                    td = $(`<td></td>`);
                    td.append(tbl);
                    tr.append(td);
                    list2table(val[`success`], tbl.find(`thead`), tbl.find(`tbody`));
                }
                else if(val && val[`success`] && typeof val[`success`] == "object"){
                    tbl = mk_table_func()
                    td = $(`<td></td>`);
                    td.append(tbl);
                    tr.append(td);
                    dict2table(val[`success`], tbl.find(`thead`), tbl.find(`tbody`));
                }
                else if(val && Array.isArray(val) && val.length > 0 && typeof val[0] == "object"){
                    tbl = mk_table_func()
                    td = $(`<td></td>`);
                    td.append(tbl);
                    tr.append(td);
                    list2table(val, tbl.find(`thead`), tbl.find(`tbody`));
                }
                else{
                    tr.append($(`<td>${val}</td>`));
                }
            });
        });
    }
    // dict型の結果をテーブルに変換
    dict2table = (data, table_head, table_body, output_image) => {
        tr = $(`<tr></tr>`);
        if(output_image){
            if(table_head)table_head.append($(`<th scope="col">output_image</th>`));
            img = $(`<img class="img-thumbnail">`).attr(`src`, `data:image/png;base64,${output_image}`);
            img.css(`width`,`100px`).css(`height`,`auto`);
            anchor = $(`<a href="data:image/jpeg;base64,${output_image}" data-lightbox="output_image"></a>`).append(img);
            tr.append($(`<td></td>`).append(anchor));
        }
        $.each(data, (key, val) => {
            if(table_head)table_head.append($(`<th scope="col">${key}</th>`));
            if (key != `warn` && val) {
                if (typeof value === 'object' || Array.isArray(val)) {
                    val = JSON.stringify(val);
                }
                if ((typeof val === `string` || val instanceof String) && val.length > 150) {
                    val = `${val.substring(0, 150)}...`;
                }
            }
            tr.append($(`<td>${val}</td>`));
        });
        table_body.append(tr);
    }
    // 結果をテーブルに変換
    if(result[`success`] && Array.isArray(result[`success`])){
        list2table(result[`success`], table_head, table_body);
    }
    else if(result[`success`] && typeof result[`success`] == "object"){
        dict2table(result[`success`], table_head, table_body, result[`output_image`]);
    }
    else if(Array.isArray(result)){
        list2table(result, table_head, table_body);
    }
    else if(typeof result === "string" || result instanceof String){
        $(`#result_modal`).find(`.modal-body`).html(result);
    }
    else {
        dict2table(result, table_head, table_body);
    }
    result_modal.modal(`show`);
}
