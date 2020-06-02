import {CorpusMC} from './corpusMC';
import {ExerciseMC} from './exerciseMC';
import {PartOfSpeechValue} from './enum';
import {ApplicationState} from './applicationState';
import {TextData} from './textData';
import {TestResultMC} from './testResultMC';
import StatementBase from './xAPI/StatementBase';
import Result from './xAPI/Result';
import Score from './xAPI/Score';
import {TextRange} from './textRange';
import {AnnisResponse, FrequencyItem} from '../../../openapi';
import {Phenomenon} from '../../../openapi';

export default class MockMC {
    static apiResponseCorporaGet: CorpusMC[] = [{
        author: 'author',
        source_urn: 'urn',
        title: 'title',
    }];
    static apiResponseFrequencyAnalysisGet: FrequencyItem[] = [{
        phenomena: [Phenomenon.Upostag],
        values: [PartOfSpeechValue.adjective.toString()]
    }];
    static apiResponseTextGet: AnnisResponse = {
        graph_data: {
            nodes: [{udep_lemma: 'lemma', annis_tok: 'tok'}],
            links: []
        }
    };
    static applicationState: ApplicationState = new ApplicationState({
        currentSetup: new TextData({
            currentCorpus: {citations: {}, source_urn: 'exampleUrn'},
            currentTextRange: new TextRange({start: ['1', '2'], end: ['1', '2']})
        }),
        mostRecentSetup: new TextData({
            annisResponse: {
                graph_data: {
                    nodes: [{}], links: []
                }
            }
        }),
        exerciseList: [new ExerciseMC()]
    });
    static popoverController: any = {create: () => Promise.resolve({present: () => Promise.resolve()})};
    static testResults: { [exerciseIndex: number]: TestResultMC } = {
        20: new TestResultMC({
            statement: new StatementBase({result: new Result({score: new Score({scaled: 0, raw: 0})})})
        })
    };
    static toastController: any = {create: () => Promise.resolve({present: () => Promise.resolve()})};

    static addIframe(h5pIframeString: string, buttonClass: string = null): HTMLIFrameElement {
        const iframe: HTMLIFrameElement = document.createElement('iframe');
        iframe.setAttribute('id', h5pIframeString.slice(1));
        document.body.appendChild(iframe);
        if (buttonClass) {
            const button: HTMLButtonElement = iframe.contentWindow.document.createElement('button');
            button.classList.add(buttonClass.slice(1));
            iframe.contentWindow.document.body.appendChild(button);
        }
        return document.querySelector(h5pIframeString);
    }
}
