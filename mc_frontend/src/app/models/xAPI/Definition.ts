import Extensions from './Extensions';
import LanguageMap from './LanguageMap';

class Definition {
    readonly name?: LanguageMap;
    readonly description?: LanguageMap;
    readonly extensions?: Extensions;
    readonly type?: string;
    readonly moreInfo?: string;
    readonly choices?: { description: LanguageMap, id: string }[];
    readonly correctResponsesPattern?: string[];
    readonly interactionType?: string;

    constructor(init?: Partial<Definition>) {
        Object.assign(this, init);
    }
}

export default Definition;
