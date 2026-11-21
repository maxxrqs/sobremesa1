# Échantillon du lot C : 2 situations × 5 langues (A1 marché, A2 gare)
# n = réplique du personnage ; i = consigne (fr) ; m = réponse modèle ; va = variantes acceptées ; o = 3 réponses fausses ; kw = mots-clés exigés à l'écrit
SIT = {}
I_MKT = ["Salue et demande six oranges.", "Demande aussi du fromage.", "Demande le prix du fromage.",
         "Dis que c'est tout et demande combien ça fait.", "Demande si tu peux payer par carte.", "Remercie et dis au revoir."]
I_TRN = ["Dis que tu as raté le train de dix heures.", "Demande à quelle heure part le prochain train.",
         "Demande si tu peux utiliser ton billet.", "Accepte et demande si tu peux payer par carte.",
         "Dis que tu vas rentrer dimanche.", "Remercie et dis au revoir."]
META = {
 "a1mercado": (1, "Au marché", "Tu fais tes courses au marché : des oranges et du fromage.", "Vendeuse", I_MKT),
 "a2tren": (2, "Le train est parti", "Tu arrives à la gare trop tard : ton train est déjà parti.", "Guichetier", I_TRN),
}
SIT["es"] = {
 "a1mercado": ([
  ("Buenos días, ¿qué desea?", "Buenos días, seis naranjas, por favor.", ["Hola, seis naranjas, por favor.", "Buenos días, quiero seis naranjas."], ["Buenas noches, seis naranjas, de nada.", "Buenos días, me llamo seis naranjas.", "Adiós, seis naranjas, gracias."], "seis;naranjas"),
  ("Aquí tiene. ¿Algo más?", "Sí, también quiero queso.", ["Sí, queso también, por favor.", "Sí, quiero queso, por favor."], ["Sí, también soy queso.", "No, también quiero queso.", "Sí, el queso está en la playa."], "queso"),
  ("El queso es muy bueno hoy.", "¿Cuánto cuesta?", ["¿Cuánto cuesta el queso?", "¿Cuánto es?"], ["¿Cuánto tiempo?", "¿Dónde cuesta?", "¿Cuándo cuesta el queso?"], "cuánto"),
  ("Cuesta seis euros.", "Vale. No, nada más, gracias. ¿Cuánto es?", ["Nada más, gracias. ¿Cuánto es?", "No, nada más. ¿Cuánto es?"], ["Sí, nada más, por favor.", "Nada más, gracias. ¿Dónde es?", "Vale, todo, gracias. ¿Quién es?"], "nada;más"),
  ("Son ocho euros.", "¿Puedo pagar con tarjeta?", ["¿Se puede pagar con tarjeta?", "¿Puedo pagar con tarjeta, por favor?"], ["¿Puedo comer con tarjeta?", "¿Puedes pagar con tarjeta?", "¿Puedo pagar sin tarjeta?"], "pagar;tarjeta"),
  ("Sí, puede pagar con tarjeta. Gracias, ¡hasta luego!", "Gracias a usted. ¡Hasta luego!", ["Muchas gracias. ¡Adiós!", "Gracias. ¡Hasta luego!"], ["De nada. ¡Buenos días!", "Lo siento. ¡Hola!", "Por favor. ¡Hasta luego!"], "gracias"),
 ], [("la naranja", "l'orange"), ("el queso", "le fromage"), ("¿Algo más?", "Autre chose ?"), ("¿Cuánto cuesta?", "Combien ça coûte ?")]),
 "a2tren": ([
  ("Buenos días, ¿en qué puedo ayudarle?", "Buenos días. He perdido el tren de las diez.", ["Perdí el tren de las diez.", "Buenos días, he perdido el tren de las diez."], ["Buenos días. Voy a perder el tren de las diez.", "Buenos días. He perdido el tren de las diez años.", "Buenos días. Pierdo el tren mañana."], "perdido;tren"),
  ("No pasa nada.", "¿A qué hora sale el próximo tren?", ["¿Cuándo sale el próximo tren?", "¿A qué hora sale el siguiente tren?"], ["¿A qué hora llegó el tren de ayer?", "¿Qué hora es el próximo tren?", "¿Dónde sale el próximo tren?"], "hora;sale"),
  ("El próximo tren sale a las once y media.", "¿Puedo usar mi billete?", ["¿Puedo usar el billete?", "¿Vale mi billete?"], ["¿Puedo usar mi billete ayer?", "¿Puedes comer mi billete?", "¿Puedo usar mi billete de nada?"], "billete"),
  ("Sí, pero tiene que pagar cinco euros más.", "Vale. ¿Puedo pagar con tarjeta?", ["De acuerdo. ¿Puedo pagar con tarjeta?", "Vale, ¿se puede pagar con tarjeta?"], ["Vale. ¿Puedo pagar con tren?", "No. ¿He pagado con tarjeta?", "Vale. ¿Puedo pagar con tarjeta anoche?"], "pagar;tarjeta"),
  ("Sí, claro. ¿Va a volver hoy?", "No, voy a volver el domingo.", ["No, vuelvo el domingo.", "No, el domingo."], ["No, volví el domingo.", "Sí, voy a volver el domingo pasado.", "No, voy a volver ayer."], "domingo"),
  ("Muy bien. Aquí tiene su billete. ¡Buen viaje!", "Muchas gracias. ¡Hasta luego!", ["Gracias. ¡Adiós!", "Muchas gracias, adiós."], ["De nada. ¡Buen viaje!", "Lo siento mucho. ¡Hola!", "Por favor. ¡Buenos días!"], "gracias"),
 ], [("perder el tren", "rater le train"), ("el próximo tren", "le prochain train"), ("el billete", "le billet"), ("¡Buen viaje!", "Bon voyage !")]),
}
SIT["va"] = {
 "a1mercado": ([
  ("Bon dia, què vol?", "Bon dia, sis taronges, per favor.", ["Hola, sis taronges, per favor.", "Bon dia, vull sis taronges."], ["Bona nit, sis taronges, de res.", "Bon dia, em dic sis taronges.", "Adéu, sis taronges, gràcies."], "sis;taronges"),
  ("Ací té. Alguna cosa més?", "Sí, també vull formatge.", ["Sí, formatge també, per favor.", "Sí, vull formatge, per favor."], ["Sí, també soc formatge.", "No, també vull formatge.", "Sí, el formatge està en la platja."], "formatge"),
  ("El formatge és molt bo hui.", "Quant costa?", ["Quant costa el formatge?", "Quant és?"], ["Quant de temps?", "On costa?", "Quan costa el formatge?"], "quant"),
  ("Costa sis euros.", "D'acord. No, res més, gràcies. Quant és?", ["Res més, gràcies. Quant és?", "No, res més. Quant és?"], ["Sí, res més, per favor.", "Res més, gràcies. On és?", "D'acord, tot, gràcies. Qui és?"], "res;més"),
  ("Són huit euros.", "Puc pagar amb targeta?", ["Es pot pagar amb targeta?", "Puc pagar amb targeta, per favor?"], ["Puc menjar amb targeta?", "Pots pagar amb targeta?", "Puc pagar sense targeta?"], "pagar;targeta"),
  ("Sí, pot pagar amb targeta. Gràcies, fins després!", "Gràcies a vosté. Fins després!", ["Moltes gràcies. Adéu!", "Gràcies. Fins després!"], ["De res. Bon dia!", "Ho sent. Hola!", "Per favor. Fins després!"], "gràcies"),
 ], [("la taronja", "l'orange"), ("el formatge", "le fromage"), ("Alguna cosa més?", "Autre chose ?"), ("Quant costa?", "Combien ça coûte ?")]),
 "a2tren": ([
  ("Bon dia, en què puc ajudar-lo?", "Bon dia. He perdut el tren de les deu.", ["Vaig perdre el tren de les deu.", "Bon dia, he perdut el tren de les deu."], ["Bon dia. Vaig a perdre el tren de les deu.", "Bon dia. He perdut el tren de les deu anys.", "Bon dia. Perd el tren demà."], "perdut;tren"),
  ("No passa res.", "A quina hora ix el pròxim tren?", ["Quan ix el pròxim tren?", "A quina hora ix el tren següent?"], ["A quina hora va arribar el tren d'ahir?", "Quina hora és el pròxim tren?", "On ix el pròxim tren?"], "hora;ix"),
  ("El pròxim tren ix a les onze i mitja.", "Puc utilitzar el meu bitllet?", ["Puc fer servir el meu bitllet?", "Val el meu bitllet?"], ["Puc utilitzar el meu bitllet ahir?", "Pots menjar el meu bitllet?", "Puc utilitzar el meu bitllet de res?"], "bitllet"),
  ("Sí, però ha de pagar cinc euros més.", "D'acord. Puc pagar amb targeta?", ["Val. Puc pagar amb targeta?", "D'acord, es pot pagar amb targeta?"], ["D'acord. Puc pagar amb tren?", "No. He pagat amb targeta?", "D'acord. Puc pagar amb targeta ahir a la nit?"], "pagar;targeta"),
  ("Sí, clar. Tornarà hui?", "No, tornaré diumenge.", ["No, torne diumenge.", "No, diumenge."], ["No, vaig tornar diumenge.", "Sí, tornaré diumenge passat.", "No, tornaré ahir."], "diumenge"),
  ("Molt bé. Ací té el seu bitllet. Bon viatge!", "Moltes gràcies. Fins després!", ["Gràcies. Adéu!", "Moltes gràcies, adéu."], ["De res. Bon viatge!", "Ho sent molt. Hola!", "Per favor. Bon dia!"], "gràcies"),
 ], [("perdre el tren", "rater le train"), ("el pròxim tren", "le prochain train"), ("el bitllet", "le billet"), ("Bon viatge!", "Bon voyage !")]),
}
SIT["ca"] = {
 "a1mercado": ([
  ("Bon dia, què vol?", "Bon dia, sis taronges, si us plau.", ["Hola, sis taronges, si us plau.", "Bon dia, vull sis taronges."], ["Bona nit, sis taronges, de res.", "Bon dia, em dic sis taronges.", "Adeu, sis taronges, gràcies."], "sis;taronges"),
  ("Aquí té. Alguna cosa més?", "Sí, també vull formatge.", ["Sí, formatge també, si us plau.", "Sí, vull formatge, si us plau."], ["Sí, també sóc formatge.", "No, també vull formatge.", "Sí, el formatge és a la platja."], "formatge"),
  ("El formatge és molt bo avui.", "Quant costa?", ["Quant costa el formatge?", "Quant és?"], ["Quant de temps?", "On costa?", "Quan costa el formatge?"], "quant"),
  ("Costa sis euros.", "D'acord. No, res més, gràcies. Quant és?", ["Res més, gràcies. Quant és?", "No, res més. Quant és?"], ["Sí, res més, si us plau.", "Res més, gràcies. On és?", "D'acord, tot, gràcies. Qui és?"], "res;més"),
  ("Són vuit euros.", "Puc pagar amb targeta?", ["Es pot pagar amb targeta?", "Puc pagar amb targeta, si us plau?"], ["Puc menjar amb targeta?", "Pots pagar amb targeta?", "Puc pagar sense targeta?"], "pagar;targeta"),
  ("Sí, pot pagar amb targeta. Gràcies, fins després!", "Gràcies a vostè. Fins després!", ["Moltes gràcies. Adeu!", "Gràcies. Fins després!"], ["De res. Bon dia!", "Ho sento. Hola!", "Si us plau. Fins després!"], "gràcies"),
 ], [("la taronja", "l'orange"), ("el formatge", "le fromage"), ("Alguna cosa més?", "Autre chose ?"), ("Quant costa?", "Combien ça coûte ?")]),
 "a2tren": ([
  ("Bon dia, en què el puc ajudar?", "Bon dia. He perdut el tren de les deu.", ["Vaig perdre el tren de les deu.", "Bon dia, he perdut el tren de les deu."], ["Bon dia. Vaig a perdre el tren de les deu.", "Bon dia. He perdut el tren de les deu anys.", "Bon dia. Perdo el tren demà."], "perdut;tren"),
  ("No passa res.", "A quina hora surt el pròxim tren?", ["Quan surt el pròxim tren?", "A quina hora surt el tren següent?"], ["A quina hora va arribar el tren d'ahir?", "Quina hora és el pròxim tren?", "On surt el pròxim tren?"], "hora;surt"),
  ("El pròxim tren surt a les onze i mitja.", "Puc fer servir el meu bitllet?", ["Puc utilitzar el meu bitllet?", "Val el meu bitllet?"], ["Puc fer servir el meu bitllet ahir?", "Pots menjar el meu bitllet?", "Puc fer servir el meu bitllet de res?"], "bitllet"),
  ("Sí, però ha de pagar cinc euros més.", "D'acord. Puc pagar amb targeta?", ["Val. Puc pagar amb targeta?", "D'acord, es pot pagar amb targeta?"], ["D'acord. Puc pagar amb tren?", "No. He pagat amb targeta?", "D'acord. Puc pagar amb targeta ahir a la nit?"], "pagar;targeta"),
  ("Sí, és clar. Tornarà avui?", "No, tornaré diumenge.", ["No, torno diumenge.", "No, diumenge."], ["No, vaig tornar diumenge.", "Sí, tornaré diumenge passat.", "No, tornaré ahir."], "diumenge"),
  ("Molt bé. Aquí té el seu bitllet. Bon viatge!", "Moltes gràcies. Fins després!", ["Gràcies. Adeu!", "Moltes gràcies, adeu."], ["De res. Bon viatge!", "Ho sento molt. Hola!", "Si us plau. Bon dia!"], "gràcies"),
 ], [("perdre el tren", "rater le train"), ("el pròxim tren", "le prochain train"), ("el bitllet", "le billet"), ("Bon viatge!", "Bon voyage !")]),
}
SIT["gl"] = {
 "a1mercado": ([
  ("Bos días, que desexa?", "Bos días, seis laranxas, por favor.", ["Ola, seis laranxas, por favor.", "Bos días, quero seis laranxas."], ["Boas noites, seis laranxas, de nada.", "Bos días, chámome seis laranxas.", "Adeus, seis laranxas, grazas."], "seis;laranxas"),
  ("Aquí ten. Algo máis?", "Si, tamén quero queixo.", ["Si, queixo tamén, por favor.", "Si, quero queixo, por favor."], ["Si, tamén son queixo.", "Non, tamén quero queixo.", "Si, o queixo está na praia."], "queixo"),
  ("O queixo é moi bo hoxe.", "Canto custa?", ["Canto custa o queixo?", "Canto é?"], ["Canto tempo?", "Onde custa?", "Cando custa o queixo?"], "canto"),
  ("Custa seis euros.", "Vale. Non, nada máis, grazas. Canto é?", ["Nada máis, grazas. Canto é?", "Non, nada máis. Canto é?"], ["Si, nada máis, por favor.", "Nada máis, grazas. Onde é?", "Vale, todo, grazas. Quen é?"], "nada;máis"),
  ("Son oito euros.", "Podo pagar con tarxeta?", ["Pódese pagar con tarxeta?", "Podo pagar con tarxeta, por favor?"], ["Podo comer con tarxeta?", "Podes pagar con tarxeta?", "Podo pagar sen tarxeta?"], "pagar;tarxeta"),
  ("Si, pode pagar con tarxeta. Grazas, ata logo!", "Grazas a vostede. Ata logo!", ["Moitas grazas. Adeus!", "Grazas. Ata logo!"], ["De nada. Bos días!", "Síntoo. Ola!", "Por favor. Ata logo!"], "grazas"),
 ], [("a laranxa", "l'orange"), ("o queixo", "le fromage"), ("Algo máis?", "Autre chose ?"), ("Canto custa?", "Combien ça coûte ?")]),
 "a2tren": ([
  ("Bos días, en que podo axudalo?", "Bos días. Perdín o tren das dez.", ["Perdín o tren das dez.", "Bos días, perdín o tren das dez."], ["Bos días. Vou perder o tren das dez.", "Bos días. Perdín o tren das dez anos.", "Bos días. Perdo o tren mañá."], "perdín;tren"),
  ("Non pasa nada.", "A que hora sae o próximo tren?", ["Cando sae o próximo tren?", "A que hora sae o seguinte tren?"], ["A que hora chegou o tren de onte?", "Que hora é o próximo tren?", "Onde sae o próximo tren?"], "hora;sae"),
  ("O próximo tren sae ás once e media.", "Podo usar o meu billete?", ["Podo usar o billete?", "Vale o meu billete?"], ["Podo usar o meu billete onte?", "Podes comer o meu billete?", "Podo usar o meu billete de nada?"], "billete"),
  ("Si, pero ten que pagar cinco euros máis.", "Vale. Podo pagar con tarxeta?", ["De acordo. Podo pagar con tarxeta?", "Vale, pódese pagar con tarxeta?"], ["Vale. Podo pagar con tren?", "Non. Paguei con tarxeta?", "Vale. Podo pagar con tarxeta onte á noite?"], "pagar;tarxeta"),
  ("Si, claro. Vai volver hoxe?", "Non, vou volver o domingo.", ["Non, volvo o domingo.", "Non, o domingo."], ["Non, volvín o domingo.", "Si, vou volver o domingo pasado.", "Non, vou volver onte."], "domingo"),
  ("Moi ben. Aquí ten o seu billete. Boa viaxe!", "Moitas grazas. Ata logo!", ["Grazas. Adeus!", "Moitas grazas, adeus."], ["De nada. Boa viaxe!", "Síntoo moito. Ola!", "Por favor. Bos días!"], "grazas"),
 ], [("perder o tren", "rater le train"), ("o próximo tren", "le prochain train"), ("o billete", "le billet"), ("Boa viaxe!", "Bon voyage !")]),
}
SIT["eu"] = {
 "a1mercado": ([
  ("Egun on, zer nahi duzu?", "Egun on, sei laranja, mesedez.", ["Kaixo, sei laranja, mesedez.", "Egun on, sei laranja nahi dut."], ["Gabon, sei laranja, ez horregatik.", "Egun on, sei laranja deitzen naiz.", "Agur, sei laranja, eskerrik asko."], "sei;laranja"),
  ("Hemen duzu. Beste zerbait?", "Bai, gazta ere nahi dut.", ["Bai, gazta ere bai, mesedez.", "Bai, gazta nahi dut, mesedez."], ["Bai, ni ere gazta naiz.", "Ez, gazta ere nahi dut.", "Bai, gazta hondartzan dago."], "gazta"),
  ("Gazta ona da.", "Zenbat balio du?", ["Zenbat balio du gaztak?", "Zenbat da?"], ["Zenbat ordu?", "Non balio du?", "Noiz balio du gaztak?"], "zenbat"),
  ("Sei euro balio du.", "Ados. Ez, besterik ez, eskerrik asko. Zenbat da?", ["Besterik ez, eskerrik asko. Zenbat da?", "Ez, besterik ez. Zenbat da?", "Ez, ezer gehiago ez. Zenbat da?"], ["Bai, besterik ez, mesedez.", "Besterik ez, eskerrik asko. Non da?", "Ados, dena, eskerrik asko. Nor da?"], "zenbat"),
  ("Zortzi euro dira.", "Hemen duzu.", ["Hemen dituzu.", "Tori, hemen duzu."], ["Hemen naiz.", "Han duzu atzo.", "Hemen duzu, ez horregatik."], "hemen", "Donne l'argent : dis « voilà »."),
  ("Eskerrik asko. Gero arte!", "Eskerrik asko zuri. Gero arte!", ["Eskerrik asko. Agur!", "Mila esker. Gero arte!"], ["Ez horregatik. Egun on!", "Barkatu. Kaixo!", "Mesedez. Gero arte!"], "eskerrik"),
 ], [("laranja", "l'orange"), ("gazta", "le fromage"), ("Beste zerbait?", "Autre chose ?"), ("Zenbat balio du?", "Combien ça coûte ?")]),
 "a2tren": ([
  ("Egun on, zertan lagun zaitzaket?", "Egun on. Hamarretako trena galdu dut.", ["Hamarretako trena galdu dut.", "Egun on, hamarretako trena galdu dut."], ["Egun on. Hamarretako trena galduko dut.", "Egun on. Hamarretako trena galdu duzu.", "Egun on. Bihar trena galtzen dut."], "trena;galdu"),
  ("Lasai.", "Zer ordutan irteten da hurrengo trena?", ["Noiz irteten da hurrengo trena?", "Zer ordutan dago hurrengo trena?"], ["Zer ordutan iritsi zen atzoko trena?", "Zer ordu da hurrengo trena?", "Non irteten da hurrengo trena?"], "ordutan;trena"),
  ("Hurrengo trena hamaika eta erdietan irteten da.", "Nire txartelak balio du?", ["Txartelak balio du?", "Nire txartela erabil dezaket?"], ["Nire txartelak atzo balio du?", "Nire txartela jaten duzu?", "Nire txartelak ez horregatik balio du?"], "txartelak"),
  ("Bai, baina bost euro gehiago ordaindu behar duzu.", "Ados. Txartelarekin ordaindu ahal dut?", ["Ondo. Txartelarekin ordaindu ahal dut?", "Ados, txartelaz ordain daiteke?", "Txartelarekin ordaindu ahal dut?"], ["Ados. Trenarekin ordaindu ahal dut?", "Ez. Txartelarekin ordaindu dut?", "Ados. Atzo txartelarekin ordaindu ahal dut?"], "txartelarekin;ordaindu"),
  ("Bai, noski. Gaur itzuliko zara?", "Ez, igandean itzuliko naiz.", ["Ez, igandean itzultzen naiz.", "Ez, igandean."], ["Ez, igandean itzuli nintzen.", "Bai, igandean itzuli naiz.", "Ez, atzo itzuliko naiz."], "igandean"),
  ("Oso ondo. Hemen duzu zure txartela. Bidaia ona!", "Eskerrik asko. Gero arte!", ["Mila esker. Agur!", "Eskerrik asko, agur."], ["Ez horregatik. Bidaia ona!", "Barkatu. Kaixo!", "Mesedez. Egun on!"], "eskerrik"),
 ], [("trena galdu", "rater le train"), ("hurrengo trena", "le prochain train"), ("txartela", "le billet"), ("Bidaia ona!", "Bon voyage !")]),
}
