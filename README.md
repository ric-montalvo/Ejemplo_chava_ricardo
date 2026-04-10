Pues bueno shavales lo prometido es deuda, este programa carga una imagen hace una operacion rapida y guarda el resultado de esta misma
Esta organizado en un mvc, deben centrarse en el modelo y en el controlador
funcionan con un pipeline para que la imagen llegue al modelo, es importante que sigan esta logica.
de momento quiero que se centren unicamente en poder modificar la vista sin romper el controlador ni el modelo
PASOS >
  1. Uso del programa
    1.1.  Ejecuten el Main.py y seleccionen una imagen de prueba
    1.2.  Comprueben que en la UI se muestren 3 imagenes (original, grises y grises invertidos), maximizen la ventana para ver todo
    1.3.  Comprueben que se haya guardado de forma automatica la imagen imvertida en su PC, deberia estar en la misma ruta y tener
     casi el mismo nombre pero con el sufijo _invertida, pj, perro_invertida
  2. Estudio
    2.1. Lean la clase Vista y Controlador, no necesitan entender al 100% preguntenle a gpt o gemini, es importante que de esto entiendan
     la comunicacion entre la vista y el controlador
    2.2  Investiguen diseño de interfaz con tktinker que es la biblio que estoy usando actualmente, si tienen otra en mente
      o una forma más sencilla hagánlo como quieran pero SIN PERDER LA COMUNICACION CON EL CONTROLADOR
  3. Diseño
    3.1. Programen solo la UI de carga de imagenes, basicamente lo que les mande pero con el diseño que propusimos
