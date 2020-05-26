import {CorpusMC} from 'src/app/models/corpusMC';
import {TextRange} from 'src/app/models/textRange';
import {Author} from 'src/app/models/author';
import {AnnisResponse} from '../../../openapi';

export class TextData {
    public annisResponse: AnnisResponse;
    public currentAuthor: Author;
    public currentCorpus: CorpusMC;
    public currentTextRange: TextRange;
    public currentUrn: string;

    constructor(init?: Partial<TextData>) {
        Object.assign(this, init);
    }
}
