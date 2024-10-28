package Prom_without_Prom;
import java.io.File;
import java.util.Collection;
import java.util.HashMap;
import java.util.HashSet;
import java.util.Hashtable;
import java.util.List;
import java.util.concurrent.Future;

import org.deckfour.xes.classification.XEventClass;
import org.deckfour.xes.classification.XEventClasses;
import org.deckfour.xes.classification.XEventClassifier;
import org.deckfour.xes.info.XLogInfo;
import org.deckfour.xes.info.XLogInfoFactory;
import org.deckfour.xes.info.impl.XLogInfoImpl;
import org.deckfour.xes.model.XLog;
import org.deckfour.xes.out.XesXmlSerializer;
import org.deckfour.xes.out.XSerializer;
import org.processmining.models.connections.GraphLayoutConnection;
import org.processmining.models.graphbased.directed.petrinet.Petrinet;
import org.processmining.models.graphbased.directed.petrinet.PetrinetGraph;
import org.processmining.models.graphbased.directed.petrinet.elements.Place;
import org.processmining.models.graphbased.directed.petrinet.elements.Transition;
import org.processmining.models.graphbased.directed.petrinet.impl.PetrinetFactory;
import org.processmining.models.semantics.petrinet.Marking;
import org.processmining.plugins.connectionfactories.logpetrinet.TransEvClassMapping;
import org.processmining.plugins.pnml.base.FullPnmlElementFactory;
import org.processmining.plugins.pnml.base.Pnml;
import org.xmlpull.v1.XmlPullParser;
import org.xmlpull.v1.XmlPullParserException;
import org.xmlpull.v1.XmlPullParserFactory;

import com.fasterxml.jackson.databind.ObjectMapper;

import java.io.InputStream;
import java.io.PrintWriter;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.io.FileInputStream;
import java.io.FileNotFoundException;
import java.io.FileOutputStream;
import java.io.IOException;



// SELBER GESCHRIEBEN 
import Prom_without_Prom.ReplayerResultList;
import nl.tue.alignment.Progress;
import nl.tue.alignment.ReplayerParameters;
import nl.tue.alignment.TraceReplayTask;


public class Prom_without_Prom_Helper {
	
	public static  XLog readSingleLog(File initialFile) throws Exception {
		InputStream inputStream = new FileInputStream(initialFile);
		org.xeslite.parser.XesLiteXmlParser parser = new
		org.xeslite.parser.XesLiteXmlParser(true);
		List<XLog> parsedLogs = parser.parse(inputStream);
		if (parsedLogs.size() > 0) {
		return parsedLogs.get(0);
		}
		return null;
		}
	
	public static void exportSingleLog(XLog log, String targetName) throws IOException {
		FileOutputStream out = new FileOutputStream(targetName);
		XSerializer logSerializer = new XesXmlSerializer();
		logSerializer.serialize(log, out);
		out.close();
		}

	
	public static Pnml importPnmlFromStream(InputStream input,
			String filename, long fileSizeInBytes) throws
			XmlPullParserException, IOException {
			FullPnmlElementFactory pnmlFactory = new FullPnmlElementFactory();
			XmlPullParserFactory factory = XmlPullParserFactory.newInstance();
			factory.setNamespaceAware(true);
			XmlPullParser xpp = factory.newPullParser();
			xpp.setInput(input, null);
			int eventType = xpp.getEventType();
			Pnml pnml = new Pnml();
			synchronized (pnmlFactory) {
			pnml.setFactory(pnmlFactory);
			/*
			* Skip whatever we find until we've found a start tag.
			*/
			while (eventType != XmlPullParser.START_TAG) {
			eventType = xpp.next();
			}
			/*
			* Check whether start tag corresponds to PNML start tag.
			*/
			if (xpp.getName().equals(Pnml.TAG)) {
				/*
				* Yes it does. Import the PNML element.
				*/
				pnml.importElement(xpp, pnml);
				} else {
				/*
				* No it does not. Return null to signal failure.
				*/
				pnml.log(Pnml.TAG, xpp.getLineNumber(), "Expected pnml");
				}
				if (pnml.hasErrors()) {
				return null;
				}
				return pnml;
				}
				}
	
	
	public static Object[] connectNet(Pnml pnml, PetrinetGraph net) {
		/*
		* Return the net and the marking.
		*/
		Marking marking = new Marking();
		Collection<Marking> finalMarkings = new HashSet<Marking>();
		GraphLayoutConnection layout = new GraphLayoutConnection(net);
		pnml.convertToNet(net, marking, finalMarkings, layout);
		Object[] objects = new Object[2];
		objects[0] = net;
		objects[1] = marking;
		return objects;
		}

	
	public static Object[] importFromStream(InputStream input,
			String filename, long fileSizeInBytes) throws
			XmlPullParserException, IOException {
			Pnml pnml = importPnmlFromStream(input, filename, fileSizeInBytes);
			if (pnml == null) {
			/*
			* No PNML found in file. Fail.
			*/
			return null;
			}
			PetrinetGraph net = PetrinetFactory.newPetrinet(pnml.getLabel());
			return connectNet(pnml, net);
			}
	
	public static Object[] importFromFile(File model, String filename) throws Exception {
	return importFromStream(new FileInputStream(model), filename,
	model.length());
	}

	public static TransEvClassMapping constructMapping(PetrinetGraph net, XLog log,
			XEventClass dummyEvClass,
			XEventClassifier eventClassifier, boolean createDummy) {
			TransEvClassMapping mapping = new TransEvClassMapping(eventClassifier,
			dummyEvClass);
			XLogInfo summary = XLogInfoFactory.createLogInfo(log, eventClassifier);
			for (Transition t : net.getTransitions()) {
			boolean mapped = false;
			for (XEventClass evClass : summary.getEventClasses().getClasses()) {
			String id = evClass.getId();
			String label = t.getLabel()+"+complete";
			//id = id.substring(0, id.length()-1);
			if (label.equalsIgnoreCase(id)) {
			mapping.put(t, evClass);
			mapped = true;
			break;
			}
			}
			if (createDummy & !mapped) {
				mapping.put(t, dummyEvClass);
				mapped = true;
			}
			}
			return mapping;
			}

	public static Marking getFinalMarking(PetrinetGraph net) {
		Marking finalMarking = new Marking();
	
		for (Place p : net.getPlaces()) {
			if (net.getOutEdges(p).isEmpty())
				finalMarking.add(p);
		}
	
		return finalMarking;
	}
	
	public static Marking getInitialMarking(PetrinetGraph net) {
		Marking initMarking = new Marking();
	
		for (Place p : net.getPlaces()) {
			if (net.getInEdges(p).isEmpty())
				initMarking.add(p);
		}
	
		return initMarking;
	}


		
	public static String exportPetrinetToPNMLorEPNMLString(PetrinetGraph net, Pnml.PnmlType
			type, Marking marking) {
			Collection<Marking> finalMarkings = new HashSet<Marking>();
			GraphLayoutConnection layout;
			layout = new GraphLayoutConnection(net);
			HashMap<PetrinetGraph, Marking> markedNets = new HashMap<PetrinetGraph,
			Marking>();
			HashMap<PetrinetGraph, Collection<Marking>> finalMarkedNets = new
			HashMap<PetrinetGraph, Collection<Marking>>();
			markedNets.put(net, marking);
			finalMarkedNets.put(net, finalMarkings);
			Pnml pnml = new Pnml();
			FullPnmlElementFactory factory = new FullPnmlElementFactory();
			synchronized (factory) {
			pnml.setFactory(factory);
			pnml = pnml.convertFromNet(markedNets, finalMarkedNets, layout);
			}
			return "<?xml version=\"1.0\" encoding=\"ISO-8859-1\"?>\n" +
			pnml.exportElement(pnml);
			}
	public static void exportPetrinetToPNMLorEPNMLFile(PetrinetGraph net, Pnml.PnmlType
			type, Marking marking, String targetName) throws FileNotFoundException {
			PrintWriter out = new PrintWriter(targetName);
			out.write(exportPetrinetToPNMLorEPNMLString(net, type, marking));
			out.flush();
			out.close();
			}

}

