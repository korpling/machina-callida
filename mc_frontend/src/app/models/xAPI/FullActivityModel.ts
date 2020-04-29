import LanguageMap from './LanguageMap';
import Extensions from './Extensions';

interface FullActivityModel {
  readonly activityId: string;
  readonly name: LanguageMap;
  readonly description: LanguageMap;
  readonly moreInfo?: string;
  readonly type?: string;
  readonly extensions: Extensions;
  readonly organisationId: string;
  readonly lrsId: string;
}

export default FullActivityModel;
