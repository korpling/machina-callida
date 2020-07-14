import {Component, OnInit} from '@angular/core';
import {Author} from 'src/app/models/author';
import {NavController} from '@ionic/angular';
import {TranslateService} from '@ngx-translate/core';
import {CorpusService} from 'src/app/corpus.service';
import {HttpClient} from '@angular/common/http';
import {HelperService} from '../helper.service';
import {ExerciseService} from '../exercise.service';
import {ApplicationState} from '../models/applicationState';
import {take} from 'rxjs/operators';
import configMC from '../../configMC';

/**
 * Generated class for the AuthorPage page.
 *
 * See https://ionicframework.com/docs/components/#navigation for more info on
 * Ionic pages and navigation.
 */

@Component({
    selector: 'app-author',
    templateUrl: './author.page.html',
    styleUrls: ['./author.page.scss'],
})
export class AuthorPage implements OnInit {
    constructor(public navCtrl: NavController,
                public translate: TranslateService,
                public corpusService: CorpusService,
                public http: HttpClient,
                public exerciseService: ExerciseService,
                public helperService: HelperService) {
    }

    public authorsDisplayed: Author[];
    public baseAuthorList: Author[];
    showOnlyTreebanks = true;
    currentSearchValue = '';

    static filterAuthor(author: Author, filterValue: string): boolean {
        return author.name.toLowerCase().includes(filterValue.toLowerCase());
    }

    getAuthors(newSearchValue: string): void {
        this.baseAuthorList = this.showOnlyTreebanks ? this.getAuthorsFiltered() : this.corpusService.availableAuthors;
        if (!newSearchValue) {
            this.authorsDisplayed = this.baseAuthorList;
        } else {
            this.authorsDisplayed = this.baseAuthorList.filter((author: Author) => {
                return AuthorPage.filterAuthor(author, newSearchValue);
            });
        }
    }

    getAuthorsFiltered(): Author[] {
        return this.corpusService.availableAuthors.filter(author => author.corpora.some(corpus => this.corpusService.isTreebank(corpus)));
    }

    ngOnInit(): void {
        if (!this.corpusService.availableAuthors.length) {
            this.corpusService.loadCorporaFromLocalStorage().then(() => {
                this.toggleTreebankAuthors();
            });
        } else {
            this.toggleTreebankAuthors();
        }
    }

    restoreLastSetup(): Promise<void> {
        return new Promise<void>((resolve, reject) => {
            this.corpusService.restoreLastCorpus().then(() => {
                if (this.helperService.isVocabularyCheck) {
                    this.helperService.goToPage(this.navCtrl, configMC.pageUrlVocabularyCheck).then();
                    return resolve();
                } else {
                    this.helperService.goToShowTextPage(this.navCtrl).then();
                    return resolve();
                }
            }, () => {
                return reject();
            });
        });
    }

    showCorpora(author: Author): void {
        this.corpusService.currentAuthor = author;
        this.helperService.applicationState.pipe(take(1)).subscribe((as: ApplicationState) => {
            as.currentSetup.currentAuthor = author;
            this.helperService.saveApplicationState(as).then();
            this.helperService.goToPage(this.navCtrl, configMC.pageUrlAuthorDetail).then();
        });
    }

    toggleTreebankAuthors(): void {
        this.baseAuthorList = this.showOnlyTreebanks ? this.getAuthorsFiltered() : this.corpusService.availableAuthors;
        this.authorsDisplayed = this.baseAuthorList.filter((author: Author) => {
            return AuthorPage.filterAuthor(author, this.currentSearchValue);
        });
    }
}
