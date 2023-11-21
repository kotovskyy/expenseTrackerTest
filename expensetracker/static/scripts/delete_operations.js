function deleteTransaction(transaction_id) {

    let confirmDelete = confirm("Are you sure you want to delete this transaction?\nThis transaction cannot be restored.");
    if (confirmDelete) {
        let form = document.getElementById("deleteTransactionForm_" + transaction_id);
        form.submit();   
    }
}

function deleteCategory(category_id, ntranscations) {
    let confirmDelete = confirm("Are you sure you want to delete this category?\n All transactions ("+ntranscations+") associated with this category will be removed.");
    if (confirmDelete) {
        let form = document.getElementById("deleteCategoryForm_"+category_id);
        form.submit();
    }
}
