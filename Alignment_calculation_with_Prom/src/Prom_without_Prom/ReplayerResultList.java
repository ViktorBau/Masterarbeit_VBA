package Prom_without_Prom;

import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.ExecutionException;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;

import org.deckfour.xes.classification.XEventClasses;
import org.deckfour.xes.model.XLog;
import org.deckfour.xes.model.XTrace;
import org.processmining.models.graphbased.directed.petrinet.Petrinet;
import org.processmining.models.semantics.petrinet.Marking;
import org.processmining.plugins.connectionfactories.logpetrinet.TransEvClassMapping;
import org.processmining.plugins.petrinet.replayresult.PNRepResult;

import gnu.trove.list.TIntList;
import gnu.trove.list.array.TIntArrayList;
import nl.tue.alignment.Progress;
import nl.tue.alignment.Replayer;
import nl.tue.alignment.ReplayerParameters;
import nl.tue.alignment.TraceReplayTask;
import nl.tue.alignment.Utils;
import nl.tue.alignment.ReplayerParameters.Algorithm;
import nl.tue.alignment.Utils.Statistic;
import nl.tue.alignment.algorithms.ReplayAlgorithm.Debug;
import nl.tue.alignment.algorithms.constraints.ConstraintSet;

public class ReplayerResultList extends Replayer {

	
	


	
	private Progress progress;
	private ReplayerParameters parameters;
	private XEventClasses classes;

	public ReplayerResultList(ReplayerParameters parameters, Petrinet net, Marking initialMarking, Marking finalMarking,
			XEventClasses classes, TransEvClassMapping mapping, boolean mergeDuplicateTraces) {
		super(parameters, net, initialMarking, finalMarking, classes, mapping, mergeDuplicateTraces);
	}

	public List<Future<TraceReplayTask>> computeResultList(Progress progress, XLog log,ReplayerParameters parameters, XEventClasses classes) throws InterruptedException, ExecutionException {
		this.progress = progress;
		this.parameters = parameters;
		ConstraintSet constraintSet = null;
		this.classes = classes;
		
			

		if (parameters.debug == Debug.STATS) {
			parameters.debug.print(Debug.STATS, "SP label");
			for (Statistic s : Statistic.values()) {
				parameters.debug.print(Debug.STATS, Utils.SEP);
				parameters.debug.print(Debug.STATS, s.toString());
			}
			parameters.debug.print(Debug.STATS, Utils.SEP + "max Memory (MB)");
			parameters.debug.print(Debug.STATS, Utils.SEP + "total Memory (MB)");
			parameters.debug.print(Debug.STATS, Utils.SEP + "free Memory (MB)");

			if (parameters.algorithm == Algorithm.INCREMENTALASTAR) {
				parameters.debug.print(Debug.STATS, Utils.SEP + "Splitpoints");
			}

			parameters.debug.println(Debug.STATS);

		}


		ExecutorService service;
		//		if (parameters.algorithm == Algorithm.ASTAR) {
		//			// multi-threading is handled inside ASTAR
		//			service = Executors.newFixedThreadPool(1);
		//		} else {
		service = Executors.newFixedThreadPool(parameters.nThreads);
		//		}
		progress.setMaximum(log.size() + 1);

		List<Future<TraceReplayTask>> resultList = new ArrayList<>();

		TraceReplayTask tr = new TraceReplayTask(this, parameters, parameters.timeoutMilliseconds,
				parameters.maximumNumberOfStates, 0l);
		resultList.add(service.submit(tr));

		int t = 0;
		for (XTrace trace : log) {
			//			if (traceToInclude.length > 0
			//					&& !XConceptExtension.instance().extractName(trace).equals(traceToInclude[0])) {
			//				continue;
			//			}

			TIntList errorEvents = new TIntArrayList(trace.size());
			long preprocessTime = 0;
			if (constraintSet != null) {
				long start = System.nanoTime();
				// pre-process the trace
				constraintSet.reset();
				for (int e = 0; e < trace.size(); e++) {
					int label = class2id.get(classes.getClassOf(trace.get(e)));
					if (!constraintSet.satisfiedAfterOccurence(label)) {
						//						if (e > 0) {
						//							errorEvents.add((int) (e));
						//						}
						errorEvents.add((int) (e + 1));
					}
				}
				//				System.out.println("Splitpoints:" + errorEvents.toString());
				preprocessTime = (System.nanoTime() - start);
			}
			tr = new TraceReplayTask(this, parameters, trace, t, parameters.timeoutMilliseconds, parameters.maximumNumberOfStates,
					preprocessTime, errorEvents.toArray());
			resultList.add(service.submit(tr));
			t++;
		}

		service.shutdown();
		return resultList;
	}
	

}



































