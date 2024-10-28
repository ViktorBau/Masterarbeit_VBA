package alignment_calculation;

import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.ArrayList;
import java.util.Hashtable;
import java.util.Iterator;
import java.util.List;
import java.util.concurrent.Future;

import org.deckfour.xes.classification.XEventClass;
import org.deckfour.xes.classification.XEventClasses;
import org.deckfour.xes.classification.XEventClassifier;
import org.deckfour.xes.info.XLogInfo;
import org.deckfour.xes.info.XLogInfoFactory;
import org.deckfour.xes.info.impl.XLogInfoImpl;
import org.deckfour.xes.model.XLog;
import org.processmining.models.graphbased.directed.petrinet.Petrinet;
import org.processmining.models.graphbased.directed.petrinet.PetrinetGraph;
import org.processmining.models.graphbased.directed.petrinet.elements.Place;
import org.processmining.models.semantics.petrinet.Marking;
import org.processmining.plugins.connectionfactories.logpetrinet.TransEvClassMapping;

import com.fasterxml.jackson.databind.ObjectMapper;

import Prom_without_Prom.ReplayerResultList;
import Helper.HelperToNavigateDirectories;
import Prom_without_Prom.Prom_without_Prom_Helper;
import nl.tue.alignment.Progress;
import nl.tue.alignment.ReplayerParameters;
import nl.tue.alignment.TraceReplayTask;

public class One_optimal_alignments {

	public static void main(String[] args) throws Exception {
	
		Path pathToEventlog = Paths.get("ADD PATH TO EVENTLOG FOLDER");
	
		String nameOfEventLog = "Event_log_excluded_traces.xes";


		ArrayList all_models = HelperToNavigateDirectories.getAllModelsFromDir(pathToEventlog);

		//looping thorugh all available models
		for (int i = 0; i < all_models.size(); i++) {
			String dirModel = (String) all_models.get(i);

			System.out.println("Starting with Model: "+ dirModel);
			Path pathToModel = pathToEventlog.resolve(dirModel);
			Path pathToResult = pathToModel.resolve("PROM_alignment_results");
			 if (!Files.exists(pathToResult)) {
				 Files.createDirectories(pathToResult);
			 }
			 

			XLog log = Prom_without_Prom_Helper.readSingleLog(pathToModel.resolve(nameOfEventLog).toFile());
			Object[] petri= Prom_without_Prom_Helper.importFromFile(pathToModel.resolve("Petri_net.pnml").toFile(), "Petri_net");

			Petrinet net = (Petrinet) petri[0];
			Marking initialMarking = (Marking) petri[1];
			XEventClass dummyEvClass = new XEventClass("DUMMY", 99999);
			XEventClassifier eventClassifier = XLogInfoImpl.STANDARD_CLASSIFIER;
			TransEvClassMapping mapping = Prom_without_Prom_Helper.constructMapping(net, log, dummyEvClass,
					eventClassifier, false);


			XLog copyLog = (XLog) log.clone();

			XLogInfo summary = XLogInfoFactory.createLogInfo(log, eventClassifier);
			XEventClasses classes = summary.getEventClasses();


			Hashtable <String, ReplayerParameters>  algorithmsParamter =new Hashtable<>();
			algorithmsParamter.put("AStar", new ReplayerParameters.AStar());
			//algorithmsParamter.put("IncrementalAStar", new ReplayerParameters.IncrementalAStar());
			//algorithmsParamter.put("Dijkstra", new ReplayerParameters.Dijkstra());



			//itterate through alogrithms 
			Iterator<String> iterator = algorithmsParamter.keySet().iterator();
			while (iterator.hasNext()) {
				String algorithmName = iterator.next();
				ReplayerParameters parameters = (ReplayerParameters) algorithmsParamter.get(algorithmName);

				System.out.println("Model: "+ dirModel +" Starting Alignment for " + algorithmName);
				String fileName = "resultList_PROM_" + algorithmName+".json";
				if (!Files.exists(pathToModel.resolve(fileName))) {  
					ReplayerResultList Replayer =  new ReplayerResultList(parameters, (Petrinet) net, Prom_without_Prom_Helper.getInitialMarking(net), Prom_without_Prom_Helper.getFinalMarking(net), classes, mapping, true);



					List<Future<TraceReplayTask>> result;
					result = Replayer.computeResultList(new Progress() {

						public void setMaximum(int maximum) {
						}

						public void inc() {
						}

						public boolean isCanceled() {
							return false;
						}

						public void log(String message) {
							System.out.println(message);
						}

					}, copyLog,parameters, classes);





					Hashtable<Integer, Hashtable<String, Object>> alignmentResults = new Hashtable<>();

					for(Future<TraceReplayTask> trace: result) {
						if (trace.get().getResult().name()=="SUCCESS") {
							if (trace.get().getTraceIndex() != -1) {
								Hashtable<String, Object> traceResult = new Hashtable<>();
								traceResult.put("info",trace.get().getSuccesfulResult().getInfo() );
								traceResult.put("nodeInstance",trace.get().getSuccesfulResult().getNodeInstance().toString() );
								traceResult.put("stepTypes",trace.get().getSuccesfulResult().getStepTypes().toString() );
								alignmentResults.put(trace.get().getTraceIndex(), traceResult);
							}
						}

					}

					for(Future<TraceReplayTask> trace: result) {
						if (trace.get().getResult().name()=="DUPLICATE") {
							alignmentResults.put(trace.get().getTraceIndex(), alignmentResults.get(trace.get().getOriginalTraceIndex()));	
						}
					}


					ObjectMapper objectMapper = new ObjectMapper();
					objectMapper.writeValue(pathToResult.resolve(fileName).toFile(), alignmentResults);
				}
				else {
					System.out.println("For Model: "+ dirModel +" Alignment for " + algorithmName +"is skipped because it already exists");
				}

			}
		}

	} 







}

