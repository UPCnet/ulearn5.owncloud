Instal·lació ownCloud: /Dades/htdocs/owncloud/
Instal·lació Collabora: /usr/share/loolwsd/loleaflet/dist/

Pegats Collabora
Patch 1: Fer que el nom del document no sigui editable:

Part 1: toolbar/toolbar.js@1877

  <!-- PATCH: AFEGIT: Fer que el nom del document no sigui editable -->
  setTimeout(function () {
      var doc_name = $('#document-name-input').val();
      $('#document-name-div').text(doc_name);
  }, 5000);
<!-- END PATCH -->

Part 2: loleaflet.html@56

<!-- PATCH: AFEGIT: Fer que el nom del document no sigui editable -->
<input id="document-name-input" type="hidden" />
<div id="document-name-div"
    style="position: fixed;
    z-index: 1050;
    right: 35px;
    top: 5px;
    width: 200px;
    font-size: 16px;
    padding-right: 20px;
    border: 1px solid transparent;
    background-color: transparent;">
</div>
<!-- END PATCH -->

<!-- PATCH: ELIMINAT: Fer que el nom del document no sigui editable -->
<!--
<input id="document-name-input" type="text" />
-->
<!-- END PATCH -->

Patch 3: En clicar el botó de tancar el document, tancar la pestanya del navegador

Part 1: toolbar/toolbar.js@1866

     // PATCH: ELIMINAT: En clicar el botó de tancar el document, s'ha de tancar la pestanya del navegador
/*
$('#closebutton').click(function(e) {
  map.fire('postMessage', {msgId: 'close', args: {EverModified: map._everModified, Deprecated: true}});
  map.fire('postMessage', {msgId: 'UI_Close', args: {EverModified: map._everModified}});
  map.remove();
});
*/
// END PATCH

Part 2: loleaflet.html@85

<!-- PATCH: MODIFICAT: En clicar el botó de tancar el document, s'ha de tancar la pestanya del navegador -->
<div class="closebuttonimage"
    id="closebutton"
    style="position:absolute; top: 0px; right: 35px;"
    onclick="var window_to_close = window.open('', 'oc_window'); window_to_close.close();"
    title="Tanca el document">
</div>
<!-- ORIGINAL -->
<!--
<div class="closebuttonimage" id="closebutton"></div>
-->
<!-- END PATCH -->

Part 3: Aquest pegat requereix que, des del Plone, s’obri la finestra via javascript amb window.open i el nom de finestra ‘oc_window’

Patch 4: Eliminar la icona del Collabora de la capçalera

Part 1: loleaflet.html@40

<!-- PATCH: ELIMINAT: Eliminar la icona del Collabora de la capçalera -->
<!--
<div id="logo" class="logo"></div>
-->
<!-- END PATCH -->

Patch 5: Eliminar l’opció “Help | About” del menú

Part 1: loleaflet.html@109

<!-- PATCH: ELIMINAT: Eliminar l’opció “Help | About” del menú -->
<!--
<div id="about-dialog" style="display:none; text-align: center; user-select: text">
 <h1 id="product-name">LibreOffice Online</h1>
 <hr/>
 <h3 id="product-string"></h3>
 <p>
   <h3>LOOLWSD</h3>
   <div id="loolwsd-version"></div>
 </p>
 <p>
   <h3>LOKit</h3>
   <div id="lokit-version"></div>
 </p>
</div>
-->
<!-- END PATCH -->

Patch 6: Eliminar opció “File | Save As” del menú

Part 1: bundle.js@18253

// PATCH: ELIMINAT: Eliminar l’opció "File | Save As" del menú
/*
{name: _UNO('.uno:SaveAs', 'text'), id: 'saveas', type: 'action'},
*/
// END PATCH

Part 2: bundle.js@18464

           // PATCH: ELIMINAT: Eliminar l’opció "File | Save As" del menú
           /*
{name: _UNO('.uno:SaveAs', 'presentation'), id: 'saveas', type: 'action'},
           */
           // END PATCH

Part 3: bundle.js@18547

           // PATCH: ELIMINAT: Eliminar l’opció "File | Save As" del menú
           /*
{name: _UNO('.uno:SaveAs', 'spreadsheet'), id: 'saveas', type: 'action'},
           */
           // END PATCH



Pegats ownCloud
Patch 7: Eliminar capçalera de l’owncloud a dins el Collabora

Part 1: apps/richdocuments/css/style.css@576

/* PATCH AFEGIT: Eliminar capçalera */
#body-user #mainContainer {
   top: 0px;
}
header #header {
  display: none;
}
/* END PATCH */

Patch 8: Canvi de fons a la pantalla d’entrada:

Part 1: core/css/styles.css@29

/* PATCH: MODIFICAT: Canvi de fons a la pantalla d’entrada */
    background-color: #1d2d44;
/* ORIGINAL */
/*
    background-image: url('../img/background.jpg');
*/
/* END PATCH */

Patch 9: Canvi de logotip a la pantalla d’entrada

Part 1: Pujar la imatge nova a core/img/ amb el nom logo_upc.png

Part 2: core/css/header.css@81

/* PATCH: AFEGIT: Canvi de logotip */
#custom-login {
  background-image: url('../img/logo_upc.png');
  background-repeat: no-repeat;
  background-position: center 15px;
  background-color: #ffffff;
  width: 510px;
  height: 250px;
  margin-left: -80px;
  border: 1px solid #cccccc;
}

#body-login input[type="text"],
#body-login input[type="text"]:hover,
#body-login input[type="text"]:focus,
#body-login input[type="text"]:active,
#body-login input[type="password"],
#body-login input[type="password"]:hover,
#body-login input[type="password"]:focus,
#body-login input[type="password"]:active {
  border: 1px solid #dddddd;
  background-color: #ffffff;
  width: 247px;
}
/* END PATCH */

Part 3: core/css/header.css@108

/* PATCH: ELIMINAT: Canvi de logotip */
/*
background-image: url('../img/logo.svg');
background-repeat: no-repeat;
background-size: 175px;
background-position: center center;
width: 252px;
height: 120px;
margin: 0 auto;
*/
/* END PATCH */

Part 4: core/css/styles.css

/* PATCH: AFEGIT: Canvi de logotip */
#body-login form {
  position: absolute;
  top: 170px;
  padding: 15px;
}
/* END PATCH */


Part 5: core/templates/login.php@12

<!-- PATCH: AFEGIT: Canvi de logotip -->
<div id="custom-login" style="">
</div>
<!-- END PATCH -->

Patch 10: Eliminar text de la pantalla d’entrada

Part 1: lib/private/legacy/defaults.php@260

// PATCH AFEGIT: Fer que la funció que contrueix el peu de pàgina no retorni res
return '';
// END PATCH

Patch 11: Afegir botó per sortir de l'ownCloud

Part 1: core/templates/layout.user.php@42

<!-- PATCH AFEGIT: Afegir botó per sortir de l'ownCloud -->
<a id="logout" <?php print_unescaped(OC_User::getLogoutAttribute()); ?>
  style="position: absolute; z-index:1000; top: 9px; right: 20px;">
   <img alt=""
        src="<?php print_unescaped(image_path('', 'actions/logout_custom.svg')); ?>"
        title="<?php p($l->t('Log out')); ?>" />
</a>
<!-- END PATCH -->

Part 2: core/Controller/LoginController.php@96

// PATCH MODIFICAT: Afegir botó per sortir de l'ownCloud
     return new RedirectResponse($this->config->getSystemValue('urlcomunitats', 'https://comunitats.upc.edu'));
     // ORIGINAL
     /*
return new RedirectResponse($this->urlGenerator->linkToRouteAbsolute('core.login.showLoginForm'));
     */
     // END PATCH

Part 3: config/config.php@12

// Paràmetre afegit (URL de logout)
'urlcomunitats' => 'https://comunitats.beta.upc.edu',

Part 4: Afegir imatge core/img/actions/logout_custom.svg

Patch 12: Canvi de favicon

Part 1:
Canviar el nom del fitxer core/img/favicon.ico per core/img/favicon_orig.ico
Pujar el nou fitxer core/img/favicon.ico
