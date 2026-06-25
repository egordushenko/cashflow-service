/**
 * Зависимые select-поля: тип операции -> категория -> подкатегория.
 *
 * Используется и в форме записи (создание/редактирование), и в фильтрах списка.
 * При смене типа подгружает категории через AJAX, при смене категории —
 * подкатегории. Поддерживает восстановление выбранных значений (для edit и
 * для сохранённых фильтров после submit).
 *
 * options:
 *   operationTypeId, categoryId, subcategoryId — id select-элементов
 *   categoriesUrl, subcategoriesUrl — AJAX endpoints (можно взять из data-атрибутов)
 *   selectedCategory, selectedSubcategory — значения для восстановления
 *   includeEmptyOption — добавлять ли пункт "— все —" (для фильтров true)
 */
function initDependentSelects(options) {
    var typeEl = document.getElementById(options.operationTypeId);
    var catEl = document.getElementById(options.categoryId);
    var subEl = document.getElementById(options.subcategoryId);
    if (!typeEl || !catEl || !subEl) {
        return;
    }

    var categoriesUrl = options.categoriesUrl || typeEl.dataset.categoriesUrl;
    var subcategoriesUrl = options.subcategoriesUrl || catEl.dataset.subcategoriesUrl;
    var includeEmpty = !!options.includeEmptyOption;

    var emptyLabel = includeEmpty ? '— все —' : '---------';

    function fillSelect(selectEl, items, selectedValue) {
        selectEl.innerHTML = '';
        var empty = document.createElement('option');
        empty.value = '';
        empty.textContent = emptyLabel;
        selectEl.appendChild(empty);
        items.forEach(function (item) {
            var opt = document.createElement('option');
            opt.value = item.id;
            opt.textContent = item.name;
            if (selectedValue && String(item.id) === String(selectedValue)) {
                opt.selected = true;
            }
            selectEl.appendChild(opt);
        });
    }

    function loadCategories(selectedCategory, selectedSubcategory) {
        var typeVal = typeEl.value;
        if (!typeVal) {
            fillSelect(catEl, [], '');
            fillSelect(subEl, [], '');
            return;
        }
        fetch(categoriesUrl + '?operation_type=' + encodeURIComponent(typeVal))
            .then(function (r) { return r.json(); })
            .then(function (data) {
                fillSelect(catEl, data, selectedCategory);
                loadSubcategories(selectedSubcategory);
            });
    }

    function loadSubcategories(selectedSubcategory) {
        var catVal = catEl.value;
        if (!catVal) {
            fillSelect(subEl, [], '');
            return;
        }
        fetch(subcategoriesUrl + '?category=' + encodeURIComponent(catVal))
            .then(function (r) { return r.json(); })
            .then(function (data) {
                fillSelect(subEl, data, selectedSubcategory);
            });
    }

    typeEl.addEventListener('change', function () {
        loadCategories('', '');
    });
    catEl.addEventListener('change', function () {
        loadSubcategories('');
    });

    // Восстановление состояния при загрузке страницы, если тип уже выбран
    // (редактирование записи или применённый фильтр).
    var selCat = options.selectedCategory || catEl.dataset.selected || '';
    var selSub = options.selectedSubcategory || subEl.dataset.selected || '';
    if (typeEl.value) {
        loadCategories(selCat, selSub);
    }
}
