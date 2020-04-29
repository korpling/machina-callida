import {NgModule} from '@angular/core';
import {RouterModule, Routes} from '@angular/router';
import {IonicModule} from '@ionic/angular';
import {VocabularyCheckPage} from 'src/app/vocabulary-check/vocabulary-check.page';
import {CommonModule} from '@angular/common';
import {TranslateModule} from '@ngx-translate/core';
import {FormsModule} from '@angular/forms';

const routes: Routes = [
  {
    path: '',
    component: VocabularyCheckPage
  }
];

@NgModule({
  declarations: [
    VocabularyCheckPage,
  ],
  imports: [
    CommonModule,
    FormsModule,
    IonicModule,
    RouterModule.forChild(routes),
    TranslateModule.forChild()
  ],
})
export class VocabularyCheckPageModule {
}
