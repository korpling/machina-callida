/* tslint:disable:variable-name */
import {Solution} from 'src/app/models/solution';
import {LinkMC} from 'src/app/models/linkMC';
import {NodeMC} from 'src/app/models/nodeMC';
import {FrequencyItem} from 'src/app/models/frequencyItem';
import {TextComplexity} from 'src/app/models/textComplexity';

export class AnnisResponse {
    public directed: boolean;
    public exercise_id: string;
    public exercise_type: string;
    public frequency_analysis: FrequencyItem[];
    public links: LinkMC[];
    public multigraph: boolean;
    public nodes: NodeMC[];
    public solutions: Solution[];
    public text_complexity: TextComplexity;
    public uri: string;

    constructor(init?: Partial<AnnisResponse>) {
        Object.assign(this, init);
    }
}
