package planingBasedAlignments;
import java.util.HashSet;
import java.util.Set;
import java.util.Map.Entry;

import javax.swing.BoxLayout;
import javax.swing.JComponent;
import javax.swing.JLabel;
import javax.swing.JList;
import javax.swing.JOptionPane;
import javax.swing.JPanel;
import javax.swing.JScrollPane;

import org.deckfour.xes.classification.XEventClass;
import org.deckfour.xes.info.XLogInfo;
import org.deckfour.xes.info.XLogInfoFactory;
import org.deckfour.xes.model.XLog;
import org.deckfour.xes.model.XTrace;
import org.processmining.contexts.uitopia.UIPluginContext;
import org.processmining.datapetrinets.ui.ConfigurationUIHelper;
import org.processmining.framework.connections.ConnectionCannotBeObtained;
import org.processmining.framework.plugin.PluginDescriptor;
import org.processmining.framework.util.ui.widgets.helper.UserCancelledException;
import org.processmining.models.graphbased.directed.petrinet.Petrinet;
import org.processmining.models.graphbased.directed.petrinet.elements.Transition;
import org.processmining.models.semantics.petrinet.Marking;
import org.processmining.planningbasedalignment.plugins.planningbasedalignment.models.PlannerSearchStrategy;
import org.processmining.planningbasedalignment.plugins.planningbasedalignment.parameters.PlanningBasedAlignmentParameters;
import org.processmining.planningbasedalignment.plugins.planningbasedalignment.ui.AlignmentCostsSettingsDialog;
import org.processmining.planningbasedalignment.plugins.planningbasedalignment.ui.PlannerSettingsDialog;
import org.processmining.planningbasedalignment.plugins.planningbasedalignment.ui.PlanningBasedAlignmentConfiguration;
import org.processmining.plugins.connectionfactories.logpetrinet.TransEvClassMapping;

public class PlanningBasedAlignmentConfiguration_overwrite_VBA extends PlanningBasedAlignmentConfiguration{
	
	/**
	 * Extending PlanningBasedAlignmentConfiguration to run the function without the PROM context.
	 * 

	 */
	public PlanningBasedAlignmentParameters getParameters_no_Prom(XLog log, Petrinet petrinet, Marking initMarking,
			Marking finalMarking, TransEvClassMapping mapping) {
		


		//configureInvisibleTransitions(mapping);

		
	
		XLogInfo logInfo = XLogInfoFactory.createLogInfo(log, mapping.getEventClassifier());
		AlignmentCostsSettingsDialog moveCostCreator = new AlignmentCostsSettingsDialog(
				mapping.keySet(), logInfo.getEventClasses().getClasses());
		
		PlanningBasedAlignmentParameters parameters = new PlanningBasedAlignmentParameters();
		
		
		parameters.setPlannerSearchStrategy(PlannerSearchStrategy.BLIND_A_STAR);
		parameters.setTracesInterval(new int[]{ 1,log.size()});
		parameters.setTracesLengthBounds(getActualTracesLengthBounds(log));
		parameters.setMovesOnLogCosts(moveCostCreator.getMovesOnLogCosts());
		parameters.setMovesOnModelCosts(moveCostCreator.getMovesOnModelCosts());
		parameters.setSynchronousMovesCosts(moveCostCreator.getSynchronousMovesCosts());
		parameters.setPartiallyOrderedEvents(false);
		
		if (parameters != null) {			
			// add missing parameters
			parameters.setInitialMarking(initMarking);
			parameters.setFinalMarking(finalMarking);
			parameters.setTransitionsEventsMapping(mapping);
		}
		return parameters;
	}
	
	private void configureInvisibleTransitions(TransEvClassMapping mapping) {
		Set<Transition> unmappedTransitions = new HashSet<>();
		for (Entry<Transition, XEventClass> entry : mapping.entrySet()) {
			if (entry.getValue().equals(mapping.getDummyEventClass())) {
				if (!entry.getKey().isInvisible()) {
					unmappedTransitions.add(entry.getKey());
				}
			}
		}
		if (!unmappedTransitions.isEmpty()) {
			// specifying the Transition type makes the program crash when there are unmapped transitions
			@SuppressWarnings({ "unchecked", "rawtypes" })
			JList list = new JList(unmappedTransitions.toArray());
			
			JPanel panel = new JPanel();
			BoxLayout layout = new BoxLayout(panel, BoxLayout.Y_AXIS);
			panel.setLayout(layout);
			panel.add(new JLabel("The following transitions are not mapped to any event class:"));

			JScrollPane scrollPanel = new JScrollPane(list);
			panel.add(scrollPanel);
			panel.add(new JLabel("Do you want to consider these transitions as invisible (unlogged activities)?"));

			Object[] options = { "Yes, set them to invisible", "No, keep them as they are" };

			if (0 == JOptionPane.showOptionDialog(null, panel, "Configure transition visibility",
					JOptionPane.YES_NO_OPTION, JOptionPane.QUESTION_MESSAGE, null, options, options[0])) {
				for (Transition transition : unmappedTransitions) {
					transition.setInvisible(true);
				}
			}
		}
	}
	
	private int[] getActualTracesLengthBounds(XLog log) {
		int maxLength = 0;
		int minLength = log.get(0).size();
		int traceLength;
		for (XTrace trace : log) {
			traceLength = trace.size();
			if (traceLength > maxLength)
				maxLength = traceLength;
			if (traceLength < minLength)
				minLength = traceLength;
		}
		return new int[] { minLength, maxLength };
	}
	

}
