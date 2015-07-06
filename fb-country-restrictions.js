(function () {
    var removeCountry = function (country, txt_country) {
        var countries = document.getElementsByName('geo_gating[]');
        for (var i = 0; i < countries.length; i++) {
            if (countries[i].value == country) {
                countries[i].parentNode.removeChild(countries[i]);
            }
        }
        var txt_countries = document.getElementsByName('text_geo_gating[]');
        for (var j = 0; j < txt_countries.length; j++) {
            if (txt_countries[j].value == txt_country) {
                txt_countries[j].parentNode.removeChild(txt_countries[j]);
            }
        }
    };

    var addCountry = function (country, txt_country) {
        var inputEl = document.createElement('input');
        inputEl.type = 'hidden';
        inputEl.autocomplete = 'off';
        inputEl.name = 'geo_gating[]';
        inputEl.value = country;

        var txt_inputEl = document.createElement('input');
        txt_inputEl.type = 'hidden';
        txt_inputEl.autocomplete = 'off';
        txt_inputEl.name = 'text_geo_gating[]';
        txt_inputEl.value = txt_country;

        var geoEl = document.getElementById('geo_gating');
        geoEl.appendChild(inputEl);
        geoEl.appendChild(txt_inputEl);
    };

    var myiframe = document.createElement('iframe');
    myiframe.name = 'my_submit_target';
    document.body.appendChild(myiframe);

    var myform = document.forms[1];
    myform.target = myiframe.name;

    removeCountry('CN', 'China');
    //addCountry('CN', 'China');

    myform.submit();
})();
