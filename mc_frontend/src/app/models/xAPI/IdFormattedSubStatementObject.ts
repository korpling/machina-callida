import StatementRef from './StatementRef';
import IdFormattedActivity from './IdFormattedActivity';
import IdFormattedActor from './IdFormattedActor';

type IdFormattedSubStatementObject = (IdFormattedActivity|IdFormattedActor|StatementRef);

export default IdFormattedSubStatementObject;
