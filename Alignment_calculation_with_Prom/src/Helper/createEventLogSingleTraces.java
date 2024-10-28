package Helper;

import org.deckfour.xes.model.XLog;
import org.deckfour.xes.model.XTrace;
import org.deckfour.xes.model.impl.XLogImpl;

public class createEventLogSingleTraces {
	public static XLog createEventLogSingleTraces(XLog log, XTrace trace) {
		
		 XLog filteredLog = new XLogImpl(log.getAttributes());
		 filteredLog.add(trace);

		return filteredLog;
		
	}

}
