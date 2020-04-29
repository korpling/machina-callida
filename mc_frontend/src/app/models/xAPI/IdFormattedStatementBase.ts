import IdFormattedActor from './IdFormattedActor';
import Attachment from './Attachment';
import IdFormattedVerb from './IdFormattedVerb';
import IdFormattedContext from './IdFormattedContext';
import IdFormattedStatementObject from './IdFormattedStatementObject';
import Result from './Result';

interface IdFormattedStatementBase {
  actor: IdFormattedActor;
  object: IdFormattedStatementObject;
  verb: IdFormattedVerb;
  context?: IdFormattedContext;
  result?: Result;
  attachments?: Attachment[];
}

export default IdFormattedStatementBase;
