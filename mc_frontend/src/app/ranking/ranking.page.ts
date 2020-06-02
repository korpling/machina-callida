import {Component} from '@angular/core';
import {VocabularyService} from 'src/app/vocabulary.service';
import {ExerciseService} from 'src/app/exercise.service';
import {HelperService} from 'src/app/helper.service';
import {NavController, ToastController} from '@ionic/angular';
import {CorpusService} from 'src/app/corpus.service';
import {HttpErrorResponse} from '@angular/common/http';
import {AnnisResponse, Sentence} from '../../../openapi';

@Component({
    selector: 'app-ranking',
    templateUrl: './ranking.page.html',
    styleUrls: ['./ranking.page.scss'],
})
export class RankingPage {
    Math = Math;

    constructor(public navCtrl: NavController,
                public corpusService: CorpusService,
                public vocService: VocabularyService,
                public exerciseService: ExerciseService,
                public toastCtrl: ToastController,
                public helperService: HelperService) {
        // remove old sentence boundaries
        this.corpusService.baseUrn = this.corpusService.currentUrn.split('@')[0];
    }

    showText(rank: Sentence[]): Promise<void> {
        return new Promise<void>((resolve, reject) => {
            this.corpusService.currentUrn = this.corpusService.baseUrn + `@${rank[0].id}-${rank[rank.length - 1].id}`;
            this.vocService.getOOVwords(this.corpusService.currentUrn).then((ar: AnnisResponse) => {
                const urnStart: string = ar.graph_data.nodes[0].id.split('/')[1];
                const urnEnd: string = ar.graph_data.nodes.slice(-1)[0].id.split('/')[1];
                this.corpusService.currentUrn = urnStart.concat('-', urnEnd.split(':').slice(-1)[0]);
                this.corpusService.processAnnisResponse(ar);
                this.helperService.isVocabularyCheck = true;
                this.helperService.goToShowTextPage(this.navCtrl, true).then();
                return resolve();
            }, async (error: HttpErrorResponse) => {
                return reject();
            });
        });
    }

}
