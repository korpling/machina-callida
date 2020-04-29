import FormattedContextActivities from './FormattedContextActivities';
import IdFormattedActivity from './IdFormattedActivity';
import IdFormattedActor from './IdFormattedActor';
import Extensions from './Extensions';

interface Context {
  contextActivities?: FormattedContextActivities<IdFormattedActivity>;
  team?: IdFormattedActor;
  instructor?: IdFormattedActor;
  registration?: string;
  extensions?: Extensions;
}

export default Context;
