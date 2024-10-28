package planingBasedAlignments;

import java.util.concurrent.Executor;

import org.processmining.contexts.cli.CLIPluginContext;
import org.processmining.framework.plugin.impl.AbstractPluginContext;
import org.processmining.framework.util.ui.widgets.helper.UserCancelledException;
import org.processmining.framework.connections.ConnectionCannotBeObtained;
import org.processmining.framework.plugin.GlobalContext;
import org.processmining.framework.plugin.PluginContext;

import Prom_without_Prom.PluginContextFactory;

/**
 * Overwrites UIPluginContext from the PlaningBasedalignment Plugin to run the functions without having to use PROM 
 * 

 */

public class UIPluginContext extends AbstractPluginContext{

	static PluginContextFactory factory = new PluginContextFactory();
	static GlobalContext context = (GlobalContext)factory.getContext();
	

    public UIPluginContext(GlobalContext contextGlobal, String string) {
		super(context, "Dummy");
	}


	public void log(String message) {
        System.out.println(message);
    }

 
    public void initProgressBar() {

    }


	@Override
	public Executor getExecutor() {
		// TODO Auto-generated method stub
		return null;
	}


	@Override
	protected PluginContext createTypedChildContext(String label) {
		// TODO Auto-generated method stub
		return null;
	}

}
