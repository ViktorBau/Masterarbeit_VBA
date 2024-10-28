package Prom_without_Prom;

import org.processmining.contexts.cli.CLIPluginContext;
import org.processmining.framework.plugin.PluginContext;
import org.processmining.framework.plugin.impl.AbstractGlobalContext;
public class PluginContextFactory extends AbstractGlobalContext {
	protected PluginContext getMainPluginContext() {
	// TODO Auto-generated method stub
	return null;
	}
	public Class<? extends PluginContext> getPluginContextType() {
	// TODO Auto-generated method stub
	return null;
	}
public CLIPluginContext getContext() {
return new CLIPluginContext(this, "ciao");
}
}

